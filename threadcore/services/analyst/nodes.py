"""
Graph nodes for the analyst pipeline.

Node execution order (first question):
  preprocessor_agent → eda_agent → analyst_agent (tool-loop) → synthesis_agent

Follow-up questions skip directly to:
  analyst_agent (tool-loop) → synthesis_agent

Schema gate
-----------
analyst_agent checks state["schema_ready"] before doing anything.
If it is False (should never happen with correct routing, but defensive),
it returns an error message immediately without calling the LLM or any tool.

Tool-use loop
-------------
analyst_agent uses a ReAct-style loop:
  1. Build a system prompt that embeds the FULL df_schema.
  2. Call the LLM with bound tools.
  3. If the response contains tool_calls → execute them, append results,
     loop back to step 2.
  4. When the LLM returns plain text (no tool calls) → break; that text
     becomes the final answer passed to synthesis_agent.

Maximum 8 iterations to prevent runaway loops.
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

from threadcore.core.config import settings
from threadcore.services.analyst.state import AnalystState
from threadcore.services.analyst.preprocess import run_preprocessing
from threadcore.services.analyst.tools import (
    ANALYST_TOOLS,
    set_active_dataset,
)

# LLMs 

_llm = ChatGoogleGenerativeAI(
    model=settings.gemini_memory_model,
    temperature=0.2,
)

# LLM with tools bound (used inside analyst_agent)
_llm_with_tools = _llm.bind_tools(ANALYST_TOOLS)

MAX_TOOL_ITERATIONS = 8

# Helpers

def _build_df_schema(df: pd.DataFrame) -> dict[str, Any]:
    """
    Compact schema dict injected into every system prompt so the LLM knows
    exactly what columns exist before it picks a tool.
    """
    sample_values: dict[str, list] = {}
    for col in df.columns[:30]:           # cap at 30 columns for prompt size
        vals = df[col].dropna().unique()[:5].tolist()
        sample_values[col] = [str(v) for v in vals]

    return {
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "sample_values": sample_values,
    }


def _schema_system_prompt(schema: dict) -> str:
    col_lines = "\n".join(
        f"{col} ({schema['dtypes'].get(col, '?')})  "
        f"nulls={schema['null_counts'].get(col, 0)}  "
        f"samples={schema['sample_values'].get(col, [])}"
        for col in schema["columns"]
    )
    return (
        "You are a senior data analyst with access to four tools:\n"
        "  dataset_summary_tool  — full describe + dtypes + null counts\n"
        "  pandas_query_tool     — filter rows with df.query()\n"
        "  visualization_tool    — generate charts (bar/line/scatter/hist/box/heatmap)\n"
        "  statistical_tool      — correlation / groupby / value_counts / describe_column\n\n"
        "DATASET SCHEMA (authoritative — never invent column names):\n"
        f"  Shape: {schema['shape']['rows']} rows × {schema['shape']['cols']} cols\n"
        f"{col_lines}\n\n"
        "Rules:\n"
        "  1. ONLY use column names listed above.\n"
        "  2. Call dataset_summary_tool first if the user asks a broad question.\n"
        "  3. Always call at least one tool before writing the final answer.\n"
        "  4. Return a clear, markdown-formatted answer after you have gathered data.\n"
        "  5. When you call visualization_tool, the chart will be displayed automatically.\n"
        "     Do NOT include any image tags or base64 data in your text response.\n"
        "     Simply describe the chart in words (e.g. 'I generated a bar chart of X vs Y.').\n"
        "  6. Never output base64 strings or image data — charts are rendered separately.\n"
    )


def _execute_tool_call(tool_call: dict) -> str:
    """Dispatch a single tool_call dict to the matching LangChain tool."""
    name = tool_call["name"]
    args = tool_call.get("args", {})

    tool_map = {t.name: t for t in ANALYST_TOOLS}
    if name not in tool_map:
        return f"ERROR — unknown tool '{name}'."

    try:
        return tool_map[name].invoke(args)
    except Exception as exc:
        return f"Tool '{name}' raised an error: {exc}"


# ─────────────────────────────────────────────────────────────────────────────
# Node 1 — preprocessor_agent
# ─────────────────────────────────────────────────────────────────────────────

@traceable(name="Analyst Preprocessor")
def preprocessor_agent(state: AnalystState) -> dict:
    """Load the raw file, run the preprocessing pipeline, persist cleaned CSV."""
    path = state["dataset_path"]
    df, report_json = run_preprocessing(path)

    cleaned_path = path.rsplit(".", 1)[0] + "_cleaned.csv"
    df.to_csv(cleaned_path, index=False)

    return {
        "dataset_path": cleaned_path,
        "preprocessing_report": report_json,
        "df_json": df.head(50).to_json(orient="records"),
        "is_initialized": True,
        # schema_ready stays False until eda_agent sets it
        "schema_ready": False,
    }

# Node 2 — eda_agent

@traceable(name="Analyst EDA")
def eda_agent(state: AnalystState) -> dict:
    """Build df_schema + EDA report. Setting schema_ready=True unlocks the agent."""
    path = state["dataset_path"]
    df = pd.read_csv(path , encoding="latin1") if path.endswith(".csv") else pd.read_excel(path)

    schema = _build_df_schema(df)

    describe_full = df.describe(include="all").round(3).to_string()
    value_counts_top: dict = {}
    for col in df.select_dtypes(include=["object", "category"]).columns[:5]:
        value_counts_top[col] = df[col].value_counts().head(5).to_dict()

    eda = {
        "shape": schema["shape"],
        "columns": schema["columns"],
        "dtypes": schema["dtypes"],
        "describe": describe_full,
        "top_categorical_counts": value_counts_top,
        "null_counts": schema["null_counts"],
    }

    return {
        "eda_report": json.dumps(eda, indent=2, default=str),
        "df_schema": schema,
        "schema_ready": True,      # ← GATE OPENS HERE
    }

# Node 3 — analyst_agent  (ReAct tool-use loop)

@traceable(name="Analyst Agent")
async def analyst_agent(state: AnalystState) -> dict:
    """
    Schema-gated ReAct agent.

    The LLM is given the full df_schema in its system prompt, so it knows every
    column name and dtype BEFORE it decides which tool to call.  Tool call
    arguments are validated against the schema inside each tool, with clear
    error messages returned as ToolMessages so the LLM can self-correct.
    """
    # schema gate 
    if not state.get("schema_ready"):
        return {
            "messages": [
                AIMessage(
                    content=(
                        "Dataset schema is not yet available. "
                        "Please wait for preprocessing and EDA to complete."
                    )
                )
            ],
            "query_results": [],
        }

    schema: dict = state["df_schema"]
    dataset_path: str = state["dataset_path"]

    # Register the active dataset + schema in tools module
    set_active_dataset(dataset_path, schema)

    #  retrieve latest user question 
    user_question = "Provide a comprehensive analysis of this dataset."
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            content = str(msg.content).strip()
            if content:
                user_question = content
                break

    # build initial message list 
    system_prompt = _schema_system_prompt(schema)
    loop_messages: list = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_question),
    ]

    tool_outputs: list[dict] = []

    # ReAct loop 
    for iteration in range(MAX_TOOL_ITERATIONS):
        response: AIMessage = await _llm_with_tools.ainvoke(loop_messages)
        loop_messages.append(response)

        # No more tool calls → LLM is done
        if not response.tool_calls:
            break

        # Execute every tool call the LLM requested
        for tc in response.tool_calls:
            result_str = _execute_tool_call(tc)
            tool_outputs.append({"tool": tc["name"], "result": result_str})

            loop_messages.append(
                ToolMessage(
                    tool_call_id=tc["id"],
                    content=result_str,
                    name=tc["name"],   # required for load_analyst_conv to filter by tool
                )
            )
    else:
        # Exceeded max iterations — append a safety stop message
        loop_messages.append(
            AIMessage(
                content=(
                    "I reached the maximum number of tool calls. "
                    "Here is my analysis based on the data collected so far."
                )
            )
        )

    # Collect messages to persist in state:
    # - All AIMessages with tool_calls (so LangGraph can trace the ReAct loop)
    # - All ToolMessages (so visualizations survive checkpointing and reload)
    # - The final AIMessage (the plain-text answer)
    # We skip the opening SystemMessage and HumanMessage — they are
    # reconstructed from state on every turn and don't need to be checkpointed.
    messages_to_persist = [
        m for m in loop_messages
        if not isinstance(m, SystemMessage) and not isinstance(m, HumanMessage)
    ]

    return {
        "messages": messages_to_persist,
        "query_results": tool_outputs,
    }

# Node 4 — synthesis_agent
@traceable(name="Analyst Synthesis")
async def synthesis_agent(state: AnalystState) -> dict:
    """
    Final pass: takes the agent's tool-grounded answer and polishes it.

    If the agent already returned a thorough answer (>200 chars) this node
    passes it through unchanged to avoid a redundant LLM call.
    """
    agent_answer = ""
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, AIMessage) and msg.content:
            agent_answer = str(msg.content).strip()
            break

    # Fast-path: agent already gave a substantial answer
    if len(agent_answer) > 200:
        return {}   # no state change needed; answer already in messages

    # Short or empty answer => ask the LLM to expand using the EDA report
    preprocessing_report = state.get("preprocessing_report", "{}")
    eda_report = state.get("eda_report", "{}")

    system_msg = SystemMessage(
        content=(
            "You are a senior data analyst.\n"
            "The tool-use agent provided only a brief or empty answer.\n"
            "Use the preprocessing report and EDA report below to write a "
            "comprehensive markdown analysis covering: data quality, key statistics, "
            "distributions, outliers, correlations, and recommendations.\n"
            "Do NOT invent statistics. Only report what the reports contain."
        )
    )
    human_msg = HumanMessage(
        content=(
            f"AGENT ANSWER (expand on this):\n{agent_answer}\n\n"
            f"PREPROCESSING REPORT:\n{preprocessing_report[:4000]}\n\n"
            f"EDA REPORT:\n{eda_report[:4000]}"
        )
    )

    try:
        response = await _llm.ainvoke([system_msg, human_msg])
        content = response.content or agent_answer
    except Exception as exc:
        content = f"{agent_answer}\n\n(Synthesis failed: {exc})"

    return {"messages": [AIMessage(content=content)]}

from __future__ import annotations
import json
from typing import Any
import pandas as pd
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langsmith import traceable
from ai.core.config import settings
from ai.services.analyst.state import AnalystState
from ai.services.analyst.preprocess import run_preprocessing
from ai.services.analyst.tools import (
    ANALYST_TOOLS,
    reset_active_dataset,
    set_active_dataset,
)
from ai.services.analyst.prompts import (
    build_schema_system_prompt,
    build_synthesis_human_prompt,
    SYNTHESIS_SYSTEM_PROMPT,
)
from ai.services.context_builder import build_llm_context

# LLMs 

_llm = ChatGroq(
    model=settings.gemini_memory_model,
    api_key=settings.groq_api_key,
    temperature=0.2,
)

# LLM with tools bound (used inside analyst_agent)
_llm_with_tools = _llm.bind_tools(ANALYST_TOOLS)

MAX_TOOL_ITERATIONS = 8

# Helpers

def _build_df_schema(df: pd.DataFrame) -> dict[str, Any]:

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


def _execute_tool_call(tool_call: dict, dataset_path: str, schema: dict) -> str:
    """Dispatch a single tool_call dict to the matching LangChain tool."""
    name = tool_call["name"]
    args = tool_call.get("args", {})

    tool_map = {t.name: t for t in ANALYST_TOOLS}
    if name not in tool_map:
        return f"ERROR — unknown tool '{name}'."

    context_token = set_active_dataset(dataset_path, schema)
    try:
        return tool_map[name].invoke(args)
    except Exception as exc:
        return f"Tool '{name}' raised an error: {exc}"
    finally:
        reset_active_dataset(context_token)


def _content_for_llm_tool_message(tool_name: str, content: str) -> str:
    if tool_name != "visualization_tool":
        return content

    try:
        payload = json.loads(content)
    except Exception:
        return content

    if not isinstance(payload, dict) or payload.get("type") != "visualization":
        return content

    payload = dict(payload)
    if "image" in payload:
        payload["image"] = "[base64 image omitted from model context; visualization is persisted and displayed separately]"
    return json.dumps(payload)




@traceable(name="Analyst Preprocessor")
def preprocessor_agent(state: AnalystState) -> dict:
   
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

    #  retrieve latest user question 
    user_question = "Provide a comprehensive analysis of this dataset."
    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            content = str(msg.content).strip()
            if content:
                user_question = content
                break

    # build initial message list 
    system_prompt = build_schema_system_prompt(schema)
    loop_messages: list = build_llm_context(
        messages=state.get("messages", []),
        system_messages=SystemMessage(content=system_prompt),
        current_user_message=user_question,
        conversation_summary=state.get("conversation_summary", ""),
        important_facts=state.get("important_facts", []),
    )
    tool_outputs: list[dict] = []
    generated_messages: list[AIMessage | ToolMessage] = []

    # ReAct loop 
    for iteration in range(MAX_TOOL_ITERATIONS):
        response: AIMessage = await _llm_with_tools.ainvoke(loop_messages)
        loop_messages.append(response)
        generated_messages.append(response)

        # No more tool calls → LLM is done
        if not response.tool_calls:
            break

        # Execute every tool call the LLM requested
        for tc in response.tool_calls:
            result_str = _execute_tool_call(tc, dataset_path, schema)
            tool_outputs.append({"tool": tc["name"], "result": result_str})

            tool_message = ToolMessage(
                tool_call_id=tc["id"],
                content=result_str,
                name=tc["name"],   # required for load_analyst_conv to filter by tool
            )
            loop_messages.append(
                ToolMessage(
                    tool_call_id=tc["id"],
                    content=_content_for_llm_tool_message(tc["name"], result_str),
                    name=tc["name"],
                )
            )
            generated_messages.append(tool_message)
    else:
        # Exceeded max iterations — append a safety stop message
        safety_message = AIMessage(
            content=(
                "I reached the maximum number of tool calls. "
                "Here is my analysis based on the data collected so far."
            )
        )
        loop_messages.append(safety_message)
        generated_messages.append(safety_message)


    return {
        "messages": generated_messages,
        "query_results": tool_outputs,
    }

# Node 4 — synthesis_agent
@traceable(name="Analyst Synthesis")
async def synthesis_agent(state: AnalystState) -> dict:

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

    system_msg = SystemMessage(content=SYNTHESIS_SYSTEM_PROMPT)
    human_msg = HumanMessage(
        content=build_synthesis_human_prompt(
            agent_answer=agent_answer,
            preprocessing_report=preprocessing_report,
            eda_report=eda_report,
        )
    )

    try:
        response = await _llm.ainvoke(
            build_llm_context(
                messages=state.get("messages", []),
                system_messages=system_msg,
                current_user_message=human_msg,
                conversation_summary=state.get("conversation_summary", ""),
                important_facts=state.get("important_facts", []),
            )
        )
        content = response.content or agent_answer
    except Exception as exc:
        content = f"{agent_answer}\n\n(Synthesis failed: {exc})"

    return {"messages": [AIMessage(content=content)]}

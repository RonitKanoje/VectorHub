import json
import re
import pandas as pd
from langsmith import traceable
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
import httpx

from threadcore.core.config import settings
from threadcore.services.analyst.state import AnalystState
from threadcore.services.analyst.preprocess import run_preprocessing

# ─────────────────────────────────────
# LLM Setup
# ─────────────────────────────────────
llm = ChatOllama(
    model=settings.ollama_chat_model,
    base_url=settings.ollama_base_url,
    temperature=0.3,
)

llm_sync = ChatOllama(
    model=settings.ollama_chat_model,
    base_url=settings.ollama_base_url,
    temperature=0.3,
)

def load_df(path: str) -> pd.DataFrame:
    if path.endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_excel(path)

# ─────────────────────────────────────
# Nodes
# ─────────────────────────────────────

@traceable(name="Analyst Preprocessor")
def preprocessor_agent(state: AnalystState) -> dict:
    """Load data, run preprocessing pipeline, store cleaned df preview."""
    path = state["dataset_path"]
    df, report_json = run_preprocessing(path)

    cleaned_path = path.rsplit(".", 1)[0] + "_cleaned.csv"
    df.to_csv(cleaned_path, index=False)
    df_json = df.head(50).to_json(orient="records")

    return {
        "dataset_path": cleaned_path,
        "preprocessing_report": report_json,
        "df_json": df_json,
        "is_initialized": True,
    }


@traceable(name="Analyst EDA")
def eda_agent(state: AnalystState) -> dict:
    """Build a statistical profile from the cleaned dataset."""
    path = state["dataset_path"]
    df = pd.read_csv(path)

    describe_full = df.describe(include="all").round(3).to_string()
    value_counts_top = {}
    for col in df.select_dtypes(include=["object", "category"]).columns[:5]:
        value_counts_top[col] = df[col].value_counts().head(5).to_dict()

    eda = {
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "describe": describe_full,
        "top_categorical_counts": value_counts_top,
        "null_counts": df.isnull().sum().to_dict(),
    }

    eda_report = json.dumps(eda, indent=2, default=str)
    return {"eda_report": eda_report}


@traceable(name="Analyst Insight")
def insight_agent(state: AnalystState) -> dict:
    """LLM reads the preprocessing + EDA report and proposes meaningful queries."""
    user_question = "Provide a comprehensive analysis of this dataset."
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage) and msg.content.strip():
            user_question = msg.content.strip()
            break

    system_msg = SystemMessage(content=(
        "You are a senior data analyst. "
        "Respond ONLY with a JSON array of exactly 3 pandas-compatible query strings "
        "suitable for df.eval() or df.query(). No explanation, no markdown fences. "
        'Example: ["col_a > 100", "col_b == \'X\'", "col_c.between(10, 50)"]'
    ))
    human_msg = HumanMessage(content=(
        f"USER QUESTION: {user_question}\n\n"
        f"== PREPROCESSING REPORT ==\n{state.get('preprocessing_report', 'N/A')}\n\n"
        f"== EDA REPORT ==\n{state.get('eda_report', 'N/A')}\n\n"
        f"== DATA SAMPLE (first 10 rows) ==\n{state.get('df_json', '')[:2000]}"
    ))

    response = llm_sync.invoke([system_msg, human_msg])
    raw = response.content.strip()
    raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`")

    match = re.search(r"\[.*?\]", raw, re.DOTALL)
    queries: list[str] = []
    if match:
        try:
            queries = json.loads(match.group(0))
        except json.JSONDecodeError:
            queries = []

    if not queries:
        queries = ["index >= 0"]

    return {"insight_queries": queries}


@traceable(name="Analyst Query Executor")
def query_executor(state: AnalystState) -> dict:
    """Executes LLM-proposed queries safely and captures results."""
    path = state["dataset_path"]
    df = pd.read_csv(path)
    results = []

    for q in state.get("insight_queries", []):
        try:
            try:
                result_df = df.query(q)
                result_str = f"Query: `{q}`\nRows returned: {len(result_df)}\n{result_df.head(10).to_string(index=False)}"
            except Exception:
                result_val = df.eval(q)
                result_str = f"Eval: `{q}`\nResult: {result_val.describe().to_string() if hasattr(result_val, 'describe') else str(result_val)[:500]}"
            results.append(result_str)
        except Exception as e:
            results.append(f"Query `{q}` failed: {e}")

    return {"query_results": results}


@traceable(name="Analyst Synthesis")
async def synthesis_agent(state: AnalystState) -> dict:
    """Combines all context to answer the user's question with insights."""
    user_question = "Provide a comprehensive analysis."
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage) and msg.content.strip():
            user_question = msg.content.strip()
            break

    query_block = "\n\n".join(state.get("query_results", []))
    outlier_block = ""
    try:
        pp = json.loads(state.get("preprocessing_report", "{}"))
        outliers = pp.get("outliers_detected", [])
        if outliers:
            outlier_block = "OUTLIERS DETECTED:\n" + "\n".join(
                f"  • {o['column']}: {o['outlier_count']} outliers ({o['outlier_pct']}%)"
                for o in outliers
            )
    except Exception:
        pass

    system_msg = SystemMessage(content=(
        "You are an expert Data Analyst. "
        "Answer the user's question comprehensively using the context provided. "
        "Be concise, insightful, and structured. Use markdown formatting. Include key numbers."
    ))
    human_msg = HumanMessage(content=(
        f"USER QUESTION: {user_question}\n\n"
        + (f"{outlier_block}\n\n" if outlier_block else "")
        + f"== QUERY RESULTS ==\n{query_block}\n\n"
        + f"== EDA SUMMARY ==\n{state.get('eda_report', '')[:3000]}"
    ))

    response = await llm.ainvoke([system_msg, human_msg])
    return {"messages": [AIMessage(content=response.content)]}

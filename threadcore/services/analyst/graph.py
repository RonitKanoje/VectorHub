"""
Multi-Agent Analyst LangGraph
==============================
Agents (nodes):
  1. preprocessor_agent  — loads & cleans data, builds quality report
  2. eda_agent           — generates a rich statistical profile
  3. insight_agent       — LLM reads profile → proposes 3-5 pandas query strings
  4. query_executor      — executes each query safely via pandas .query() / eval
  5. synthesis_agent     — LLM fuses all context and answers the user's question
"""
import json
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from threadcore.domains.analyst.models import DatasetDB
from threadcore.services.analyst.state import AnalystState
from threadcore.services.analyst.nodes import (
    preprocessor_agent,
    eda_agent,
    insight_agent,
    query_executor,
    synthesis_agent,
)

# ─────────────────────────────────────
# Router
# ─────────────────────────────────────
def route_after_start(state: AnalystState) -> str:
    """Skip preprocessing+EDA if dataset already initialized (follow-up questions)."""
    if state.get("is_initialized"):
        return "insight_agent"
    return "preprocessor_agent"


# ─────────────────────────────────────
# Build Graph
# ─────────────────────────────────────
workflow = StateGraph(AnalystState)

workflow.add_node("preprocessor_agent", preprocessor_agent)
workflow.add_node("eda_agent", eda_agent)
workflow.add_node("insight_agent", insight_agent)
workflow.add_node("query_executor", query_executor)
workflow.add_node("synthesis_agent", synthesis_agent)

# Routing: first question runs full pipeline; follow-ups skip preprocessing
workflow.add_conditional_edges(START, route_after_start, {
    "preprocessor_agent": "preprocessor_agent",
    "insight_agent": "insight_agent",
})
workflow.add_edge("preprocessor_agent", "eda_agent")
workflow.add_edge("eda_agent", "insight_agent")
workflow.add_edge("insight_agent", "query_executor")
workflow.add_edge("query_executor", "synthesis_agent")
workflow.add_edge("synthesis_agent", END)

analyst_app = workflow.compile()  # Checkpointer injected at call-time via config


# ─────────────────────────────────────
# Build graph with checkpointer (call once at startup)
# ─────────────────────────────────────
def build_analyst_app(checkpointer=None):
    """Re-compile the analyst graph with an optional async checkpointer."""
    return workflow.compile(checkpointer=checkpointer)


# ─────────────────────────────────────
# Streaming entry point
# ─────────────────────────────────────
async def stream_analyst_response(message: str, thread_id: str, user_id: str, db: Session, app=None):
    if app is None:
        app = analyst_app  # fallback to no-checkpointer version

    dataset = (
        db.query(DatasetDB)
        .filter_by(thread_id=thread_id, user_id=user_id)
        .order_by(DatasetDB.created_at.desc())
        .first()
    )

    if not dataset:
        yield f"data: {json.dumps({'type': 'chunk', 'content': 'Please upload a CSV or Excel dataset first.'})}\n\n"
        yield "data: [DONE]\n\n"
        return

    inputs: AnalystState = {
        "messages": [HumanMessage(content=message)],
        "dataset_path": dataset.file_path,
        "df_json": "",
        "preprocessing_report": "",
        "eda_report": "",
        "insight_queries": [],
        "query_results": [],
        "is_initialized": False,
    }

    # Thread config enables PostgreSQL checkpoint persistence per session
    config = {"configurable": {"thread_id": f"analyst-{user_id}-{thread_id}"}}

    async for event in app.astream_events(inputs, config=config, version="v2"):
        kind = event["event"]
        node = event.get("metadata", {}).get("langgraph_node", "")

        # Node entry → emit a progress ping
        if kind == "on_chain_start" and node in (
            "preprocessor_agent", "eda_agent", "insight_agent",
            "query_executor", "synthesis_agent"
        ):
            labels = {
                "preprocessor_agent": "🔧 Preprocessing data…",
                "eda_agent": "📊 Running EDA…",
                "insight_agent": "💡 Generating insights…",
                "query_executor": "⚙️ Executing queries…",
                "synthesis_agent": "✍️ Synthesising answer…",
            }
            label = labels.get(node, "")
            if label:
                yield f"data: {json.dumps({'type': 'chunk', 'content': label + chr(10)})}\n\n"

        # Model streaming tokens (synthesis agent output)
        if kind == "on_chat_model_stream" and node == "synthesis_agent":
            chunk = event["data"]["chunk"].content
            if chunk and isinstance(chunk, str):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"

    yield "data: [DONE]\n\n"

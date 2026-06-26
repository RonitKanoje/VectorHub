from __future__ import annotations
import json
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session
from threadcore.domains.analyst.models import DatasetDB
from threadcore.services.analyst.profiler import format_profile_message, profile_dataset
from threadcore.services.analyst.state import AnalystState
from threadcore.services.analyst.nodes import (
    analyst_agent,
    eda_agent,
    preprocessor_agent,
    synthesis_agent,
)


# Router
def route_after_start(state: AnalystState) -> str:
    """
    First question  → is_initialized is False  → run full pipeline.
    Follow-up       → is_initialized is True   → jump straight to agent.

    NOTE: schema_ready is checked *inside* analyst_agent as a secondary guard.
    The router only decides whether to re-run the expensive preprocessing step.
    """
    if state.get("is_initialized") and state.get("schema_ready"):
        return "analyst_agent"
    return "preprocessor_agent"

# Graph definition

_workflow = StateGraph(AnalystState)

_workflow.add_node("preprocessor_agent", preprocessor_agent)
_workflow.add_node("eda_agent", eda_agent)
_workflow.add_node("analyst_agent", analyst_agent)
_workflow.add_node("synthesis_agent", synthesis_agent)

_workflow.add_conditional_edges(
    START,
    route_after_start,
    {
        "preprocessor_agent": "preprocessor_agent",
        "analyst_agent": "analyst_agent",
    },
)

_workflow.add_edge("preprocessor_agent", "eda_agent")
_workflow.add_edge("eda_agent", "analyst_agent")
_workflow.add_edge("analyst_agent", "synthesis_agent")
_workflow.add_edge("synthesis_agent", END)

# Compiled without checkpointer — injected at call-time via config
analyst_app = _workflow.compile()


def build_analyst_app(checkpointer=None):
    """Re-compile with an optional async checkpointer (call once at startup)."""
    return _workflow.compile(checkpointer=checkpointer)


# Streaming entry point

# Progress labels shown to the user as SSE chunks
_PROGRESS_LABELS: dict[str, str] = {
    "preprocessor_agent": "Preprocessing data…",
    "eda_agent":          "Running exploratory analysis…",
    "analyst_agent":      "Agent thinking and running tools…",
    "synthesis_agent":    "Synthesising final answer…",
}


async def stream_analyst_response(
    message: str,
    thread_id: str,
    user_id: str,
    db: Session,
    app=None,
):
    """
    Async generator that yields SSE-formatted chunks.

    Chunk types:
      {"type": "profile",  "content": "markdown banner"}  — dataset accepted (pre-graph)
      {"type": "progress", "content": "label text"}        — node started
      {"type": "chunk",    "content": "token text"}        — LLM token
      {"type": "tool",     "content": "tool name: result snippet"}
      [DONE]
    """
    if app is None:
        app = analyst_app

    # resolve dataset 
    dataset = (
        db.query(DatasetDB)
        .filter_by(thread_id=thread_id, user_id=user_id)
        .order_by(DatasetDB.created_at.desc())
        .first()
    )

    if not dataset:
        yield _sse({"type": "chunk", "content": "Please upload a CSV or Excel dataset first."})
        yield "data: [DONE]\n\n"
        return

    # ── profile the file (cheap, sync, runs before the graph) ────────────────
    # This gives us: row/col counts, missing-value summary, memory usage.
    # On first question we emit it as a confirmation banner before the pipeline
    # starts.  On follow-ups it is already in state (checkpointer) so we skip.
    try:
        dataset_profile = profile_dataset(dataset.file_path)
        profile_msg = format_profile_message(dataset_profile)
        yield _sse({"type": "profile", "content": profile_msg})
    except Exception as exc:
        dataset_profile = {}
        yield _sse({"type": "chunk", "content": f"Could not profile dataset: {exc}\n"})

    # initial state 
    inputs: AnalystState = {
        "messages":             [HumanMessage(content=message)],
        "dataset_path":         dataset.file_path,
        "dataset_profile":      dataset_profile,
        "df_json":              "",
        "preprocessing_report": "",
        "eda_report":           "",
        "df_schema":            {},
        "query_results":        [],
        "is_initialized":       False,
        "schema_ready":         False,
    }

    config = {"configurable": {"thread_id": f"analyst-{user_id}-{thread_id}"}}

    # event stream 
    async for event in app.astream_events(inputs, config=config, version="v2"):
        kind = event["event"]
        node = event.get("metadata", {}).get("langgraph_node", "")

        # Node entry → progress ping
        if kind == "on_chain_start" and node in _PROGRESS_LABELS:
            yield _sse({"type": "progress", "content": _PROGRESS_LABELS[node]})

        # LLM streaming tokens (from analyst_agent or synthesis_agent)
        # Guard: skip any chunk that looks like base64 image data — the LLM
        # should never emit these, but this acts as a final safety net.
        if kind == "on_chat_model_stream" and node in ("analyst_agent", "synthesis_agent"):
            chunk_content = event["data"]["chunk"].content
            if chunk_content and isinstance(chunk_content, str):
                # Drop chunks that are part of a data URI (base64 leaking into text)
                if "data:image" not in chunk_content and "base64," not in chunk_content:
                    yield _sse({"type": "chunk", "content": chunk_content})

        # Tool execution completed inside analyst_agent
        if kind == "on_tool_end" and node == "analyst_agent":
            tool_name = event.get("name", "")
            raw_output = event["data"].get("output", "")

            # Normalise: LangGraph may wrap the return value in various ways
            if hasattr(raw_output, "content"):
                output_str = raw_output.content
            elif isinstance(raw_output, str):
                output_str = raw_output
            else:
                output_str = json.dumps(raw_output) if raw_output else ""

            if tool_name == "visualization_tool":
                try:
                    vis_data = json.loads(output_str)
                    if isinstance(vis_data, dict) and vis_data.get("type") == "visualization":
                        yield _sse(vis_data)
                except Exception:
                    pass
                # Don't send a text preview for visualizations — the image IS the preview
                continue

            # For all other tools: send a brief activity preview
            preview = output_str[:120].replace("\n", " ")
            yield _sse({"type": "tool", "content": f"{tool_name}: {preview}…"})

    yield "data: [DONE]\n\n"


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"

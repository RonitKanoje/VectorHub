import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from ai.api.dependencies import get_current_user, CurrentUser
from ai.infrastructure.db.session import get_db
from ai.domains.analyst.models import DatasetDB
from ai.services.analyst.profiler import profile_dataset
from ai.services.analyst.graph import get_initial_analyst_state, load_analyst_conversation
from ai.services.chat.llm_config import llm as context_llm
from ai.services.context_builder import schedule_context_cache_refresh
from ai.services.rag.thread_service import (
    get_user_thread,
    save_or_update_thread,
)

router = APIRouter(tags=["analyst"])
logger = logging.getLogger(__name__)


class AnalystChatRequest(BaseModel):
    message: str
    thread_id: str


# Progress labels shown to the user as SSE chunks
PROGRESS_LABELS: dict[str, str] = {
    "preprocessor_agent": "Preprocessing data…",
    "eda_agent":          "Running exploratory analysis…",
    "analyst_agent":      "Agent thinking and running tools…",
    "synthesis_agent":    "Synthesising final answer…",
}


def sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/analyst_chat")
async def analyst_chat(
    request: AnalystChatRequest,
    req: Request,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Ensure thread exists
    thread = get_user_thread(db, request.thread_id, current_user.user_id)

    if thread is None:
        save_or_update_thread(
            db,
            request.thread_id,
            "New Analyst Chat",
            current_user.user_id,
            mode="analyst"
        )

    analyst_app = getattr(req.app.state, "analyst_app", None)
    if not analyst_app:
         raise HTTPException(
            status_code=500,
            detail="Analyst app not initialized in state"
        )

    async def event_generator():
        # resolve dataset
        dataset = (
            db.query(DatasetDB)
            .filter_by(thread_id=request.thread_id, user_id=current_user.user_id)
            .order_by(DatasetDB.created_at.desc())
            .first()
        )

        if not dataset:
            yield sse({"type": "chunk", "content": "Please upload a CSV or Excel dataset first."})
            yield "data: [DONE]\n\n"
            return

        dataset_profile = {}
        try:
            dataset_profile = profile_dataset(dataset.file_path)
        except Exception as exc:
            logger.exception("Dataset profiling failed")

        # initial state
        inputs = get_initial_analyst_state(
            message=request.message,
            dataset_path=dataset.file_path,
            dataset_profile=dataset_profile,
        )

        config = {"configurable": {"thread_id": f"analyst-{current_user.user_id}-{request.thread_id}"}}

        # event stream
        async for event in analyst_app.astream_events(inputs, config=config, version="v2"):
            kind = event["event"]
            node = event.get("metadata", {}).get("langgraph_node", "")

            if kind == "on_chain_start" and node in PROGRESS_LABELS:
                yield sse({"type": "progress", "content": PROGRESS_LABELS[node]})

            if kind == "on_chat_model_stream" and node in ("analyst_agent", "synthesis_agent"):
                chunk_content = event["data"]["chunk"].content
                if chunk_content and isinstance(chunk_content, str):
                    # Drop chunks that are part of a data URI (base64 leaking into text)
                    if "data:image" not in chunk_content and "base64," not in chunk_content:
                        yield sse({"type": "chunk", "content": chunk_content})

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
                            yield sse(vis_data)
                    except Exception:
                        pass
                    # Don't send a text preview for visualizations — the image IS the preview
                    continue

                # For all other tools: send a brief activity preview
                preview = output_str[:120].replace("\n", " ")
                yield sse({"type": "tool", "content": f"{tool_name}: {preview}…"})

        schedule_context_cache_refresh(
            app=analyst_app,
            config=config,
            llm=context_llm,
            as_node="synthesis_agent",
        )

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@router.get("/load_analyst_conv/{thread_id}")
async def load_analyst_conv(
    thread_id: str,
    req: Request,
    current_user: CurrentUser = Depends(get_current_user)
):

    analyst_app = getattr(req.app.state, "analyst_app", None)

    if not analyst_app:
        return {"messages": []}

    messages = await load_analyst_conversation(analyst_app, thread_id, current_user.user_id)
    return {"messages": messages}

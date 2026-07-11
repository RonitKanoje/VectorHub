import os
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from threadcore.infrastructure.db.session import get_db
from threadcore.services.analyst.dataset_service import process_and_save_dataset
from threadcore.services.analyst.graph import stream_analyst_response

from threadcore.services.rag.thread_service import (
    get_user_thread,
    save_or_update_thread,
)

router = APIRouter()


class ProcessDatasetRequest(BaseModel):
    media: str
    thread_id: str
    path: str
    language: str | None = None
    document_name: str | None = None


import os
import traceback
from fastapi import Depends, Header, HTTPException

@router.post("/process_dataset")
async def process_dataset(
    request: ProcessDatasetRequest,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
):
    print("\n========== PROCESS DATASET START ==========")
    print(f"User ID       : {x_user_id}")
    print(f"Thread ID     : {request.thread_id}")
    print(f"Document Name : {request.document_name}")
    print(f"File Path     : {request.path}")

    if not x_user_id:
        print("ERROR: Missing X-User-Id header")
        raise HTTPException(
            status_code=401,
            detail="X-User-Id header missing"
        )

    print(f"Path exists   : {os.path.exists(request.path)}")

    if os.path.exists(request.path):
        print(f"File size     : {os.path.getsize(request.path)} bytes")
        print(f"Extension     : {os.path.splitext(request.path)[1]}")
    else:
        raise HTTPException(
            status_code=400,
            detail="File path does not exist"
        )

    print("Checking thread...")

    thread = get_user_thread(
        db,
        request.thread_id,
        x_user_id,
    )

    print(f"Thread found  : {thread is not None}")

    if thread is None:
        print("Creating new analyst thread...")
        save_or_update_thread(
            db,
            request.thread_id,
            "New Analyst Chat",
            x_user_id,
            mode="analyst",
        )

    print("Calling process_and_save_dataset()...")

    try:
        dataset, df, report_json = process_and_save_dataset(
            db=db,
            file_path=request.path,
            thread_id=request.thread_id,
            user_id=x_user_id,
            document_name=request.document_name,
        )

        print("Dataset preprocessing completed successfully.")
        print(f"Rows          : {len(df)}")
        print(f"Columns       : {len(df.columns)}")
        print("========== PROCESS DATASET SUCCESS ==========\n")

    except Exception as e:
        print("\n========== PROCESS DATASET FAILED ==========")
        print("Exception Type :", type(e).__name__)
        print("Exception      :", str(e))
        traceback.print_exc()
        print("===========================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to preprocess dataset: {str(e)}"
        )

    return {
        "status": "success",
        "message": "Dataset preprocessed and stored",
        "rows": len(df),
        "cols": len(df.columns),
    }


class AnalystChatRequest(BaseModel):
    message: str
    thread_id: str


@router.post("/analyst_chat")
async def analyst_chat(
    request: AnalystChatRequest,
    req: Request,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db)
):
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="X-User-Id header missing"
        )

    # Ensure thread exists
    thread = get_user_thread(
        db,
        request.thread_id,
        x_user_id
    )

    if thread is None:
        save_or_update_thread(
            db,
            request.thread_id,
            "New Analyst Chat",
            x_user_id,
            mode="analyst"
        )

    analyst_app = getattr(req.app.state, "analyst_app", None)

    return StreamingResponse(
        stream_analyst_response(
            request.message,
            request.thread_id,
            x_user_id,
            db,
            app=analyst_app
        ),
        media_type="text/event-stream"
    )


@router.get("/load_analyst_conv/{thread_id}")
async def load_analyst_conv(
    thread_id: str,
    req: Request,
    x_user_id: str = Header(None)
):
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="X-User-Id header missing"
        )

    analyst_app = getattr(req.app.state, "analyst_app", None)

    if not analyst_app:
        return {"messages": []}

    config = {
        "configurable": {
            "thread_id": f"analyst-{x_user_id}-{thread_id}"
        }
    }

    state = await analyst_app.aget_state(config)

    if state is None or not state.values.get("messages"):
        return {"messages": []}

    messages = state.values["messages"]
    conversation = []

    import json

    # Each user turn produces a block of messages in this order:
    #   HumanMessage
    #   AIMessage (with tool_calls)  ← intermediate ReAct steps
    #   ToolMessage (tool result)    ← may contain visualization JSON
    #   ...                          ← more tool call/result pairs
    #   AIMessage (no tool_calls)    ← final text answer
    #
    # We want to produce:
    #   {"role": "user",      "content": "..."}
    #   {"role": "assistant", "content": "...", "visualizations": [...]}

    current_assistant: dict | None = None

    def _flush(block: dict | None):
        """Add the current assistant block to conversation if it has content."""
        if block and (block["content"] or block["visualizations"]):
            conversation.append(block)

    for message in messages:
        if message.type == "human":
            _flush(current_assistant)
            current_assistant = {"role": "assistant", "content": "", "visualizations": []}
            conversation.append({"role": "user", "content": message.content})

        elif message.type == "ai":
            if current_assistant is None:
                current_assistant = {"role": "assistant", "content": "", "visualizations": []}
            # Only the final AIMessage (no tool_calls) carries the human-readable answer
            if message.content and not message.tool_calls:
                current_assistant["content"] += message.content

        elif message.type == "tool":
            if current_assistant is None:
                current_assistant = {"role": "assistant", "content": "", "visualizations": []}
            tool_name = getattr(message, "name", "") or ""
            if tool_name == "visualization_tool":
                try:
                    vis_data = json.loads(message.content)
                    if isinstance(vis_data, dict) and vis_data.get("type") == "visualization":
                        current_assistant["visualizations"].append(vis_data)
                except Exception:
                    pass

    _flush(current_assistant)

    return {"messages": conversation}
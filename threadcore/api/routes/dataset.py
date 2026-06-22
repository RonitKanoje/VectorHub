import os
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from threadcore.infrastructure.db.session import get_db
from sqlalchemy.orm import Session
from threadcore.services.analyst.dataset_service import process_and_save_dataset
from threadcore.services.analyst.graph import stream_analyst_response

router = APIRouter()

class ProcessDatasetRequest(BaseModel):
    media: str
    thread_id: str
    path: str
    language: str | None = None

@router.post("/process_dataset")
async def process_dataset(
    request: ProcessDatasetRequest,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db)
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing")

    if not os.path.exists(request.path):
        raise HTTPException(status_code=400, detail="File path does not exist")

    try:
        dataset, df, report_json = process_and_save_dataset(
            db=db,
            file_path=request.path,
            thread_id=request.thread_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preprocess dataset: {str(e)}")

    return {"status": "success", "message": "Dataset preprocessed and stored", "rows": len(df), "cols": len(df.columns)}

class AnalystChatRequest(BaseModel):
    message: str
    thread_id: str

from fastapi.responses import StreamingResponse

@router.post("/analyst_chat")
async def analyst_chat(
    request: AnalystChatRequest,
    req: Request,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db)
):
    
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing")

    analyst_app = getattr(req.app.state, "analyst_app", None)

    return StreamingResponse(
        stream_analyst_response(request.message, request.thread_id, x_user_id, db, app=analyst_app),
        media_type="text/event-stream"
    )

@router.get("/load_analyst_conv/{thread_id}")
async def load_analyst_conv(
    thread_id: str,
    req: Request,
    x_user_id: str = Header(None)
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header missing")
        
    analyst_app = getattr(req.app.state, "analyst_app", None)
    if not analyst_app:
        return {"messages": []}

    config = {"configurable": {"thread_id": f"analyst-{x_user_id}-{thread_id}"}}
    state = await analyst_app.aget_state(config)
    
    if state is None or not state.values.get("messages"):
        return {"messages": []}
        
    messages = state.values["messages"]
    conversation = []

    for message in messages:
        if message.type == "human":
            conversation.append({"role": "user", "content": message.content})
        elif message.type == "ai":
            conversation.append({"role": "assistant", "content": message.content})

    return {"messages": conversation}


from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm import Session

from threadcore.api.dependencies import ensure_thread_access, get_current_user
from threadcore.api.schemas import ProcessMediaRequest
from threadcore.infrastructure.cache.redis_client import get_thread_status, set_thread_status
from threadcore.services.rag.thread_service import save_or_update_thread as create_or_update_thread
from threadcore.infrastructure.db.session import get_db
from threadcore.services.ingestion.pipeline import process_media_upload


router = APIRouter(tags=["ingestion"])


def _resolve_user(x_user_id: str | None = Header(default=None, alias="X-User-Id")) -> str:
    """Get current user ID from header"""
    return get_current_user(x_user_id=x_user_id)


@router.post("/process_media")
async def process_media(
    payload: ProcessMediaRequest,
    background_tasks: BackgroundTasks, ###
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    create_or_update_thread(db, payload.thread_id, "New Chat", current_user, mode="chat")
    set_thread_status(payload.thread_id, "queued")
    background_tasks.add_task(
        process_media_upload,
        payload.path,
        payload.media,
        payload.thread_id,
        current_user,
        payload.language,
        payload.document_name,
    )
    return {"status": "Processing started"}


@router.get("/ingestion_status/{thread_id}")
def ingestion_status(
    thread_id: str,
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user)
    status = get_thread_status(thread_id)
    if status is None:
        return {"status": "invalid_thread_id"}
    return {"status": status}


@router.get("/thread_status/{thread_id}")
def thread_status(
    thread_id: str,
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user)
    status = get_thread_status(thread_id)
    if status is None:
        return {"status": "chat"}
    return {"status": status}

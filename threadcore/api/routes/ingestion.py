from fastapi import APIRouter, BackgroundTasks, Depends, Header
from sqlalchemy.orm import Session

from threadcore.api.dependencies import ensure_thread_access, get_current_user
from threadcore.api.schemas import ProcessMediaRequest
from threadcore.infrastructure.cache.redis_client import redis_client
from threadcore.infrastructure.db.models import UserDB
from threadcore.infrastructure.db.repositories import create_or_update_thread
from threadcore.infrastructure.db.session import get_db
from threadcore.services.ingestion.pipeline import process_media_upload


router = APIRouter(tags=["ingestion"])


def _resolve_user(x_user_id: str = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)):
    return get_current_user(x_user_id=x_user_id, db=db)


@router.post("/process_media")
async def process_media(
    payload: ProcessMediaRequest,
    background_tasks: BackgroundTasks,
    current_user: UserDB = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    create_or_update_thread(db, payload.thread_id, "New Chat", current_user.id)
    redis_client.set(payload.thread_id, "queued")
    background_tasks.add_task(
        process_media_upload,
        payload.path,
        payload.media,
        payload.thread_id,
        current_user.id,
        payload.language,
    )
    return {"status": "Processing started"}


@router.get("/ingestion_status/{thread_id}")
def ingestion_status(
    thread_id: str,
    current_user: UserDB = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user.id)
    status = redis_client.get(thread_id)
    if status is None:
        return {"status": "invalid_thread_id"}
    return {"status": status}


@router.get("/thread_status/{thread_id}")
def thread_status(
    thread_id: str,
    current_user: UserDB = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    ensure_thread_access(db, thread_id, current_user.id)
    status = redis_client.get(thread_id)
    if status is None:
        return {"status": "invalid_thread_id"}
    return {"status": status}

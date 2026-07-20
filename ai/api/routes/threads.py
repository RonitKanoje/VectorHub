from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ai.api.dependencies import get_current_user, CurrentUser
from ai.api.schemas import ThreadResponse
from ai.services.rag.thread_service import get_user_threads
from ai.infrastructure.db.session import get_db

router = APIRouter(tags=["threads"])


@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(
    mode: str = "chat",
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
   
    threads = get_user_threads(db, current_user.user_id, mode)
    return threads

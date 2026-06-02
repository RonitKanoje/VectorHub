from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from threadcore.api.dependencies import get_current_user
from threadcore.api.schemas import ThreadResponse
from threadcore.infrastructure.db.repositories import get_threads_for_user
from threadcore.infrastructure.db.session import get_db


router = APIRouter(tags=["threads"])


def _resolve_user(x_user_id: str = Header(..., alias="X-User-Id")) -> str:
    """Get current user ID from header"""
    return get_current_user(x_user_id=x_user_id)


@router.get("/threads", response_model=List[ThreadResponse])
async def get_threads(
    current_user: str = Depends(_resolve_user),
    db: Session = Depends(get_db),
):
    return get_threads_for_user(db, current_user)

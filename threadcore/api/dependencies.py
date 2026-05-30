from fastapi import Header, HTTPException
from sqlalchemy.orm import Session

from threadcore.infrastructure.db.models import UserDB
from threadcore.infrastructure.db.repositories import get_user_by_id, get_thread_for_user
from fastapi import Request


def get_chatbot(request: Request):
    return request.app.state.chatbot


def get_current_user(
    x_user_id: str = Header(..., alias="X-User-Id"),
    db: Session = None,
) -> UserDB:
    """
    Resolve the authenticated user from the trusted X-User-Id header.
    This header is set exclusively by the Express auth middleware after
    verifying the JWT — FastAPI trusts it unconditionally.
    Never expose the FastAPI port directly to the public internet.
    """
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id header")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


def ensure_thread_access(db: Session, thread_id: str, user_id: int):
    thread = get_thread_for_user(db, thread_id, user_id)
    if thread is None:
        raise HTTPException(status_code=404, detail="invalid_thread_id")
    return thread

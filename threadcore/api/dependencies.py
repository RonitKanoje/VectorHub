from fastapi import Header, HTTPException, Request
from sqlalchemy.orm import Session
from threadcore.services.rag.thread_service import get_user_thread as get_thread_for_user


def get_chatbot(request: Request):
    return request.app.state.chatbot


def get_current_user(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    """
    Resolve the authenticated user ID from the trusted X-User-Id header.
    This header is set exclusively by the Express auth middleware after
    verifying the JWT — FastAPI trusts it unconditionally.
    User data is stored in MongoDB; this just validates the presence of the ID.
    
    Returns the MongoDB user ObjectId as a string.
    """
    if not x_user_id or x_user_id.strip() == "":
        raise HTTPException(status_code=401, detail="Invalid X-User-Id header")
    return x_user_id


def ensure_thread_access(db: Session, thread_id: str, user_id: str):
    """Verify the MongoDB user owns the thread"""
    thread = get_thread_for_user(db, thread_id, user_id) ### 
    if thread is None:
        raise HTTPException(status_code=404, detail="invalid_thread_id")
    return thread

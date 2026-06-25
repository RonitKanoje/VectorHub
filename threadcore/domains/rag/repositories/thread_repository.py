from sqlalchemy.orm import Session
from threadcore.domains.rag.models import ThreadDB


def get_threads_for_user(db: Session, user_id: str, mode: str = "chat"):
    """Get all threads for a MongoDB user (user_id is MongoDB ObjectId as string) filtered by mode"""
    return (
        db.query(ThreadDB)
        .filter(ThreadDB.user_id == user_id, ThreadDB.mode == mode)
        .order_by(ThreadDB.updated_at.desc(), ThreadDB.created_at.desc())
        .all()
    )


def get_thread_for_user(db: Session, thread_id: str, user_id: str) -> ThreadDB | None:
    """Verify user owns the thread (user_id is MongoDB ObjectId as string)"""
    return (
        db.query(ThreadDB)
        .filter(ThreadDB.thread_id == thread_id, ThreadDB.user_id == user_id)
        .first()
    )


def create_or_update_thread(db: Session, thread_id: str, title: str, user_id: str, mode: str = "chat") -> ThreadDB:
    thread = get_thread_for_user(db, thread_id, user_id)
    if thread is None:
        thread = ThreadDB(thread_id=thread_id, title=title, user_id=user_id, mode=mode)
        db.add(thread)
    else:
        thread.title = title

    db.commit()
    db.refresh(thread)
    return thread

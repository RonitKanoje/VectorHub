from sqlalchemy.orm import Session
from ai.domains.rag.repositories.thread_repository import (
    get_threads_for_user,
    get_thread_for_user,
    create_or_update_thread as repo_create_or_update_thread,
)

def get_user_threads(db: Session, user_id: str, mode: str = "chat"):
    """Service to get all threads for a user by mode."""
    return get_threads_for_user(db, user_id, mode)

def get_user_thread(db: Session, thread_id: str, user_id: str):
    """Service to get a specific thread for a user."""
    return get_thread_for_user(db, thread_id, user_id)

def save_or_update_thread(db: Session, thread_id: str, title: str, user_id: str, mode: str = "chat"):
    """Service to create or update a thread's title and mode."""
    return repo_create_or_update_thread(db, thread_id, title, user_id, mode)

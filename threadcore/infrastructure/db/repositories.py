from sqlalchemy.orm import Session

from threadcore.infrastructure.db.models import ThreadDB, UserDB


def get_user_by_id(db: Session, user_id: int) -> UserDB | None:
    return db.query(UserDB).filter(UserDB.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> UserDB | None:
    return db.query(UserDB).filter(UserDB.username == username).first()


def get_all_users(db: Session):
    return db.query(UserDB).order_by(UserDB.created_at.desc()).all()


def get_threads_for_user(db: Session, user_id: int):
    return (
        db.query(ThreadDB)
        .filter(ThreadDB.user_id == user_id)
        .order_by(ThreadDB.updated_at.desc(), ThreadDB.created_at.desc())
        .all()
    )


def get_thread_for_user(db: Session, thread_id: str, user_id: int) -> ThreadDB | None:
    return (
        db.query(ThreadDB)
        .filter(ThreadDB.thread_id == thread_id, ThreadDB.user_id == user_id)
        .first()
    )


def create_or_update_thread(db: Session, thread_id: str, title: str, user_id: int) -> ThreadDB:
    thread = get_thread_for_user(db, thread_id, user_id)
    if thread is None:
        thread = ThreadDB(thread_id=thread_id, title=title, user_id=user_id)
        db.add(thread)
    else:
        thread.title = title

    db.commit()
    db.refresh(thread)
    return thread


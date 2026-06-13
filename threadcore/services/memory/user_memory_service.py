from threadcore.infrastructure.db.session import SessionLocal
from threadcore.infrastructure.db.user_memory_repository import (
    create_memory,
    get_memories_for_user,
)


def store_user_memories(
    user_id: str,
    memories: list[str],
):
    db = SessionLocal()

    try:
        for memory in memories:
            create_memory(
                db=db,
                user_id=user_id,
                memory_text=memory,
            )
    finally:
        db.close()


def retrieve_user_memories(
    user_id: str,
):
    db = SessionLocal()

    try:
        return get_memories_for_user(
            db=db,
            user_id=user_id,
        )
    finally:
        db.close()
from threadcore.infrastructure.db.session import SessionLocal
from threadcore.domains.rag.repositories.memory_repository import (
    create_memory,
    get_memories_for_user,
)


def store_user_memories(user_id: str, memories: list[str]):
    db = SessionLocal()
    try:
        existing = get_memories_for_user(db=db, user_id=user_id)
        existing_texts = {m.memory_text.lower().strip() for m in existing}

        for memory in memories:
            if memory.lower().strip() not in existing_texts:
                create_memory(db=db, user_id=user_id, memory_text=memory)
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

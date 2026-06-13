from sqlalchemy.orm import Session

from threadcore.infrastructure.db.models import UserMemoryDB


def get_memories_for_user(
    db: Session,
    user_id: str,
):
    """Get all active memories for a user."""
    return (
        db.query(UserMemoryDB)
        .filter(
            UserMemoryDB.user_id == user_id,
            UserMemoryDB.is_deleted == False,
        )
        .order_by(
            UserMemoryDB.updated_at.desc(),
            UserMemoryDB.created_at.desc(),
        )
        .all()
    )


def create_memory(
    db: Session,
    user_id: str,
    memory_text: str,
    memory_type: str = "general",
):
    """Create a new memory."""

    memory = UserMemoryDB(
        user_id=user_id,
        memory_text=memory_text,
        memory_type=memory_type,
    )

    db.add(memory)
    db.commit()
    db.refresh(memory)

    return memory


def get_memory_by_id(
    db: Session,
    memory_id: str,
):
    """Get a memory by id."""

    return (
        db.query(UserMemoryDB)
        .filter(UserMemoryDB.id == memory_id)
        .first()
    )


def soft_delete_memory(
    db: Session,
    memory_id: str,
):
    """Soft delete a memory."""

    memory = get_memory_by_id(db, memory_id)

    if memory is None:
        return None

    memory.is_deleted = True

    db.commit()
    db.refresh(memory)

    return memory


def update_memory(
    db: Session,
    memory_id: str,
    memory_text: str,
):
    """Update an existing memory."""

    memory = get_memory_by_id(db, memory_id)

    if memory is None:
        return None

    memory.memory_text = memory_text

    db.commit()
    db.refresh(memory)

    return memory


def search_memories(
    db: Session,
    user_id: str,
    query: str,
):
    """Simple text search across memories."""

    return (
        db.query(UserMemoryDB)
        .filter(
            UserMemoryDB.user_id == user_id,
            UserMemoryDB.is_deleted == False,
            UserMemoryDB.memory_text.ilike(f"%{query}%"),
        )
        .all()
    )
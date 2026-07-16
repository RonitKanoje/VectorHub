import json
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from threadcore.domains.rag.models import (
    MemoryConflictDB,
    MemoryTopicDB,
)

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _topic_title(text: str) -> str:
    cleaned = _normalize_text(text)
    return cleaned[:70] if cleaned else "Memory"


def get_memories_for_user(db: Session, user_id: str):
    """Get active topic documents for a user."""
    return (
        db.query(MemoryTopicDB)
        .filter(
            MemoryTopicDB.user_id == user_id,
            MemoryTopicDB.is_deleted == False,
        )
        .order_by(
            MemoryTopicDB.updated_at.desc(),
            MemoryTopicDB.created_at.desc(),
        )
        .all()
    )


def get_memories_by_ids(db: Session, user_id: str, memory_ids: list[str]):
    """Get active topic documents for a user by id."""
    if not memory_ids:
        return []

    return (
        db.query(MemoryTopicDB)
        .filter(
            MemoryTopicDB.user_id == user_id,
            MemoryTopicDB.id.in_(memory_ids),
            MemoryTopicDB.is_deleted == False, ## soft deleting the memory we are not deleting it permenately
        )
        .all()
    )


def create_memory(
    db: Session,
    user_id: str,
    memory_text: str,
    memory_type: str = "general",
):
    """Create a topic document."""

    cleaned = _normalize_text(memory_text)
    if not cleaned:
        return None

    topic_obj = MemoryTopicDB(
        user_id=user_id,
        title=_topic_title(cleaned),
        summary=cleaned,
        memory_type=memory_type,

        metadata_json=json.dumps({"source": "initial_extraction"}),
    )
    db.add(topic_obj)
    db.flush()
    return topic_obj


def get_memory_by_id(db: Session, memory_id: str):
    """Get a topic by id."""
    return db.query(MemoryTopicDB).filter(MemoryTopicDB.id == memory_id).first()


def soft_delete_memory(db: Session, memory_id: str):
    """Soft delete a topic document."""
    memory = get_memory_by_id(db, memory_id)
    if memory is None:
        return None
    memory.is_deleted = True
    db.commit()
    db.refresh(memory)
    return memory


def soft_delete_memory_summary(db: Session, memory_id: str):
    """Soft delete a topic document without committing the session."""
    memory = get_memory_by_id(db, memory_id)
    if memory is None:
        return None
    memory.is_deleted = True
    memory.updated_at = datetime.utcnow()
    db.flush()
    return memory


def update_memory(db: Session, memory_id: str, memory_text: str):
    """Update an existing topic document."""
    memory = get_memory_by_id(db, memory_id)
    if memory is None:
        return None
    memory.summary = _normalize_text(memory_text)
    memory.updated_at = datetime.utcnow()
    memory.summary_version = (memory.summary_version or 1) + 1
    db.commit()
    db.refresh(memory)
    return memory


def update_memory_summary(
    db: Session,
    memory_id: str,
    memory_text: str,
):
    """Update an existing topic document without committing the session."""
    memory = get_memory_by_id(db, memory_id)
    if memory is None:
        return None
    memory.summary = _normalize_text(memory_text)
    memory.updated_at = datetime.utcnow()
    memory.evidence_count = (memory.evidence_count or 0) + 1
    memory.summary_version = (memory.summary_version or 1) + 1
    db.flush()
    return memory



def create_conflict(
    db: Session,
    user_id: str,
    topic_id: Optional[str],
    conflict_type: str,
    existing_summary: Optional[str],
    incoming_content: Optional[str],
):
    """Record a contradiction or correction for later maintenance."""
    conflict = MemoryConflictDB(
        user_id=user_id,
        topic_id=topic_id,
        conflict_type=conflict_type,
        existing_summary=existing_summary,
        incoming_content=incoming_content,
    )
    db.add(conflict)
    db.commit()
    db.refresh(conflict)
    return conflict

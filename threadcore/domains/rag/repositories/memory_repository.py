import json
import logging
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from threadcore.domains.rag.models import (
    MemoryConflictDB,
    MemoryEventDB,
    MemoryTopicDB,
    MemoryTopicEvidenceDB,
    MemoryTopicVersionDB,
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


def create_memory_event(
    db: Session,
    user_id: str,
    topic_id: str,
    memory_text: str,
    memory_type: str = "general",
):
    """Create an atomic memory event for a topic."""
    cleaned = _normalize_text(memory_text)
    if not cleaned:
        return None

    event = MemoryEventDB(
        user_id=user_id,
        topic_id=topic_id,
        event_type="fact",
        content=cleaned,
        confidence=80,
        status="consolidated",
        payload_json=json.dumps({"memory_type": memory_type}),
    )
    db.add(event)
    db.flush()

    evidence = MemoryTopicEvidenceDB(
        topic_id=topic_id,
        event_id=event.id,
        strength=1,
        source_kind="extraction",
        evidence_excerpt=cleaned,
    )
    db.add(evidence)
    return event


def create_memory_version(
    db: Session,
    topic_id: str,
    version: int,
    summary: str,
    change_reason: str = "fact_ingested",
):
    """Create a topic version snapshot."""
    snapshot = MemoryTopicVersionDB(
        topic_id=topic_id,
        version=version,
        summary=_normalize_text(summary),
        change_reason=change_reason,
        created_by="memory_service",
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def create_memory(
    db: Session,
    user_id: str,
    memory_text: str,
    memory_type: str = "general",
):
    """Create a topic document and the atomic event that led to it."""

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
    event = create_memory_event(
        db=db,
        user_id=user_id,
        topic_id=topic_obj.id,
        memory_text=cleaned,
        memory_type=memory_type,
    )
    create_memory_version(
        db=db,
        topic_id=topic_obj.id,
        version=topic_obj.summary_version or 1,
        summary=topic_obj.summary,
        change_reason="fact_ingested",
    )
    return event



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
    change_reason: str = "fact_updated",
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
    create_memory_version(
        db=db,
        topic_id=memory.id,
        version=memory.summary_version,
        summary=memory.summary,
        change_reason=change_reason,
    )
    return memory


def search_memories(db: Session, user_id: str, query: str):
    """Search topic summaries for a user."""
    return (
        db.query(MemoryTopicDB)
        .filter(
            MemoryTopicDB.user_id == user_id,
            MemoryTopicDB.is_deleted == False,
            MemoryTopicDB.summary.ilike(f"%{query}%"),
        )
        .all()
    )


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

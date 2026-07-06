import json
import re
import traceback
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
    UserMemoryDB,
)


def _normalize_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _topic_title(text: str) -> str:
    cleaned = _normalize_text(text)
    return cleaned[:70] if cleaned else "Memory"


def _token_overlap(left: str, right: str) -> float:
    left_tokens = set(re.findall(r"\w+", left.lower()))
    right_tokens = set(re.findall(r"\w+", right.lower()))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))


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

    topic = (
        db.query(MemoryTopicDB)
        .filter(
            MemoryTopicDB.user_id == user_id,
            MemoryTopicDB.is_deleted == False,
        )
        .order_by(MemoryTopicDB.updated_at.desc())
        .all()
    )

    best_match = None
    best_score = 0.0
    for candidate in topic:
        score = _token_overlap(candidate.summary, cleaned)
            
        if score > best_score and score >= 0.35:
            best_match = candidate
            best_score = score

    if best_match is None:
        topic_obj = MemoryTopicDB(
            user_id=user_id,
            title=_topic_title(cleaned),
            summary=cleaned,
            memory_type=memory_type,
            confidence_score=80,
            metadata_json=json.dumps({"source": "initial_extraction"}),
        )
        db.add(topic_obj)
        db.flush()
        topic_id = topic_obj.id
    else:
        best_match.summary = f"{best_match.summary} | {cleaned}"
        best_match.updated_at = datetime.utcnow()
        best_match.evidence_count = (best_match.evidence_count or 0) + 1
        best_match.summary_version = (best_match.summary_version or 1) + 1
        topic_id = best_match.id

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
    return event

    evidence = MemoryTopicEvidenceDB(
        topic_id=topic_id,
        event_id=event.id,
        strength=1,
        source_kind="extraction",
        evidence_excerpt=cleaned,
    )
    db.add(evidence)

    version = MemoryTopicVersionDB(
        topic_id=topic_id,
        version=(best_match.summary_version if best_match else 1),
        summary=cleaned if best_match is None else (best_match.summary or cleaned),
        change_reason="fact_ingested",
        created_by="memory_service",
    )
    db.add(version)

    try:
        db.commit()
        topic_count = db.query(func.count(MemoryTopicDB.id)).scalar()
        event_count = db.query(func.count(MemoryEventDB.id)).scalar()
        db.refresh(event)
        if best_match is None:
            db.refresh(topic_obj)
            return topic_obj
        db.refresh(best_match)
        return best_match
    except Exception:
        traceback.print_exc()
        db.rollback()
        raise


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
    event_id: Optional[str],
    conflict_type: str,
    existing_summary: Optional[str],
    incoming_content: Optional[str],
):
    """Record a contradiction or correction for later maintenance."""
    conflict = MemoryConflictDB(
        user_id=user_id,
        topic_id=topic_id,
        event_id=event_id,
        conflict_type=conflict_type,
        existing_summary=existing_summary,
        incoming_content=incoming_content,
    )
    db.add(conflict)
    db.commit()
    db.refresh(conflict)
    return conflict

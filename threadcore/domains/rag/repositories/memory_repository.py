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
    print("====================================================")
    print("ENTERED create_memory")
    print("ENTERED repository")
    print("====================================================")
    print("Session object:", db)
    print("Transaction active?", db.in_transaction())
    print("Connection:", db.connection())
    print("Transaction active after connection?", db.in_transaction())
    print("user_id:", user_id)
    print("memory_text:", memory_text)

    cleaned = _normalize_text(memory_text)
    print("Normalized memory_text:", cleaned)
    if not cleaned:
        print("EARLY RETURN: cleaned memory_text is empty before db.add()")
        print("Empty cleaned text; returning before insertion")
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
    print("Candidate topics for matching:", [(candidate.id, candidate.summary) for candidate in topic])

    best_match = None
    best_score = 0.0
    for candidate in topic:
        score = _token_overlap(candidate.summary, cleaned)
        print("Topic matching score", candidate.id, score, "for", candidate.summary)
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
        print("Creating MemoryTopic:", topic_obj)
        print("db.add(MemoryTopic)")
        db.add(topic_obj)
        print("db.flush(MemoryTopic)")
        db.flush()
        topic_id = topic_obj.id
        print("Created MemoryTopic id:", topic_id)
    else:
        best_match.summary = f"{best_match.summary} | {cleaned}"
        best_match.updated_at = datetime.utcnow()
        best_match.evidence_count = (best_match.evidence_count or 0) + 1
        best_match.summary_version = (best_match.summary_version or 1) + 1
        topic_id = best_match.id
        print("Updating existing MemoryTopic:", best_match.id)

    event = MemoryEventDB(
        user_id=user_id,
        topic_id=topic_id,
        event_type="fact",
        content=cleaned,
        confidence=80,
        status="consolidated",
        payload_json=json.dumps({"memory_type": memory_type}),
    )
    print("Creating MemoryEvent:", event)
    print("db.add(MemoryEvent)")
    db.add(event)
    print("db.flush(MemoryEvent)")
    db.flush()
    print("Created MemoryEvent id:", event.id)

    evidence = MemoryTopicEvidenceDB(
        topic_id=topic_id,
        event_id=event.id,
        strength=1,
        source_kind="extraction",
        evidence_excerpt=cleaned,
    )
    print("Creating MemoryTopicEvidence:", evidence)
    print("db.add(MemoryTopicEvidence)")
    db.add(evidence)

    version = MemoryTopicVersionDB(
        topic_id=topic_id,
        version=(best_match.summary_version if best_match else 1),
        summary=cleaned if best_match is None else (best_match.summary or cleaned),
        change_reason="fact_ingested",
        created_by="memory_service",
    )
    print("Creating MemoryTopicVersion:", version)
    print("db.add(MemoryTopicVersion)")
    db.add(version)

    try:
        print("ENTERED db.commit")
        db.commit()
        print("Commit successful")
        topic_count = db.query(func.count(MemoryTopicDB.id)).scalar()
        event_count = db.query(func.count(MemoryEventDB.id)).scalar()
        print("SELECT COUNT(*) FROM memory_topics ->", topic_count)
        print("SELECT COUNT(*) FROM memory_events ->", event_count)
        db.refresh(event)
        if best_match is None:
            db.refresh(topic_obj)
            print("Rows inserted: topic and event and evidence and version")
            print("Database row user_id:", topic_obj.user_id)
            print("EXIT create_memory")
            return topic_obj
        db.refresh(best_match)
        print("Rows inserted: event and evidence and version")
        print("Database row user_id:", best_match.user_id)
        print("EXIT create_memory")
        return best_match
    except Exception:
        print("Exception during commit in create_memory()")
        traceback.print_exc()
        db.rollback()
        print("Rollback complete in create_memory")
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

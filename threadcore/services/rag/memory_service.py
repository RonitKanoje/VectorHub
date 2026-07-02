import re
import traceback
from typing import List

from sqlalchemy import func

from threadcore.domains.rag.models import MemoryEventDB
from threadcore.domains.rag.models import MemoryTopicDB
from threadcore.domains.rag.repositories.memory_repository import (
    create_conflict,
    create_memory,
    get_memories_for_user,
)
from threadcore.infrastructure.db.session import SessionLocal


def _normalize_memory_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _token_overlap(left: str, right: str) -> float:
    left_tokens = set(re.findall(r"\w+", left.lower()))
    right_tokens = set(re.findall(r"\w+", right.lower()))
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))


def store_user_memories(user_id: str, memories: list[str]):
    """Buffer and consolidate new memories into topic documents."""
    print("====================================================")
    print("ENTERED store_user_memories")
    print("====================================================")
    print("user_id:", user_id)
    print("facts:", memories)

    db = SessionLocal()
    print("Session object:", db)
    print("Transaction active?", db.in_transaction())
    print("Connection:", db.connection())
    print("Transaction active after connection?", db.in_transaction())
    try:
        existing = get_memories_for_user(db=db, user_id=user_id)
        print("Existing topics:", [(topic.id, topic.summary) for topic in existing])

        existing_events = (
            db.query(MemoryEventDB)
            .filter(MemoryEventDB.user_id == user_id)
            .order_by(MemoryEventDB.created_at.desc())
            .all()
        )
        print("Existing events:", [(event.id, event.content, event.status) for event in existing_events])

        for memory in memories:
            normalized = _normalize_memory_text(memory)
            print("Processing memory:", normalized)
            if not normalized:
                print("EARLY RETURN: skipping empty normalized memory")
                continue

            best_match = None
            best_score = 0.0
            for topic in existing:
                score = _token_overlap(topic.summary, normalized)
                print("Topic matching score", topic.id, score, "for", topic.summary)
                if score > best_score and score >= 0.35:
                    best_match = topic
                    best_score = score

            print("Selected topic:", best_match.id if best_match else None)
            print("Creating new topic?", best_match is None)
            if best_match is not None and best_match.summary != normalized:
                print("Updating existing topic?", True)
                create_conflict(
                    db=db,
                    user_id=user_id,
                    topic_id=best_match.id,
                    event_id=None,
                    conflict_type="update",
                    existing_summary=best_match.summary,
                    incoming_content=normalized,
                )
            else:
                print("Updating existing topic?", False)

            print("Creating event?", True)
            print("Creating evidence?", True)
            print("Creating version?", True)
            print("Calling create_memory()")
            create_memory(db=db, user_id=user_id, memory_text=normalized)
            print("Returned from create_memory()")

        print("ENTERED db.commit in store_user_memories")
        db.commit()
        print("Commit successful in store_user_memories")
        print("Transaction active after commit?", db.in_transaction())

        final_topics = get_memories_for_user(db=db, user_id=user_id)
        print("Final topics after write:", [(topic.id, topic.summary) for topic in final_topics])
        final_events = (
            db.query(MemoryEventDB)
            .filter(MemoryEventDB.user_id == user_id)
            .order_by(MemoryEventDB.created_at.desc())
            .all()
        )
        print("Final events after write:", [(event.id, event.content, event.status) for event in final_events])
        topic_count = db.query(func.count(MemoryTopicDB.id)).scalar()
        event_count = db.query(func.count(MemoryEventDB.id)).scalar()
        print("SELECT COUNT(*) FROM memory_topics ->", topic_count)
        print("SELECT COUNT(*) FROM memory_events ->", event_count)
        print("EXIT store_user_memories")
    except Exception:
        print("Exception in store_user_memories()")
        traceback.print_exc()
        db.rollback()
        print("Rollback complete in store_user_memories")
        raise
    finally:
        db.close()
        print("Closed Session in store_user_memories")


def retrieve_user_memories(user_id: str):
    """Retrieve the most relevant topic documents for prompt construction."""
    db = SessionLocal()
    try:
        memories = get_memories_for_user(db=db, user_id=user_id)
        return memories[:8]
    finally:
        db.close()


def consolidate_user_memories(user_id: str):
    """Convenience entry point for periodic consolidation maintenance."""
    return store_user_memories(user_id=user_id, memories=[])


def maintain_user_memory(user_id: str):
    """Trigger scheduled maintenance on the user's memory topics."""
    return consolidate_user_memories(user_id=user_id)

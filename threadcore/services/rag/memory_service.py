import logging
import re
from typing import List

from threadcore.domains.rag.repositories.memory_repository import (
    create_conflict,
    create_memory,
    get_memories_for_user,
)
from threadcore.infrastructure.db.session import SessionLocal

logger = logging.getLogger(__name__)


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
    db = SessionLocal()
    try:
        existing = get_memories_for_user(db=db, user_id=user_id)

        for memory in memories:
            normalized = _normalize_memory_text(memory)
            if not normalized:
                continue

            best_match = None
            best_score = 0.0
            for topic in existing:
                score = _token_overlap(topic.summary, normalized)
                if score > best_score and score >= 0.35:
                    best_match = topic
                    best_score = score

            if best_match is not None and best_match.summary != normalized:
                create_conflict(
                    db=db,
                    user_id=user_id,
                    topic_id=best_match.id,
                    event_id=None,
                    conflict_type="update",
                    existing_summary=best_match.summary,
                    incoming_content=normalized,
                )
            create_memory(db=db, user_id=user_id, memory_text=normalized)

        db.commit()
    except Exception:
        logger.exception("Failed to store user memories")
        db.rollback()
        raise
    finally:
        db.close()


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

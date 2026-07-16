import logging

from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from qdrant_client.models import FieldCondition, Filter, MatchValue

from threadcore.core.config import settings
from threadcore.domains.rag.repositories.memory_repository import (
    create_conflict,
    create_memory,
    create_memory_event,
    get_memories_by_ids,
    get_memory_by_id,
    get_memories_for_user,
    soft_delete_memory_summary,
    update_memory_summary,
)
from threadcore.services.chat.llm_config import memory_reconciliation_llm
from threadcore.services.chat.prompts import memory_reconciliation_prompt
from threadcore.infrastructure.db.session import SessionLocal
from threadcore.infrastructure.vector.qdrant import create_vector_store

logger = logging.getLogger(__name__)

PERSONAL_MEMORY_COLLECTION = "PERSONAL_MEMORY_COLLECTION"
PERSONAL_MEMORY_LIMIT = 8
PERSONAL_MEMORY_CANDIDATE_LIMIT = 1


def _normalize_memory_text(text: str) -> str:
    return " ".join(text.split()).strip()


def _memory_document(memory) -> Document:
    return Document(
        page_content=memory.summary,
        metadata={
            "memory_id": str(memory.id),
            "user_id": str(memory.user_id),
            "memory_type": memory.memory_type,
            "summary_version": memory.summary_version,
        },
    )


def _index_memory(memory) -> None:
    _index_memories([memory])


def _index_memories(memories) -> None:
    if not memories:
        return

    vector_store = create_vector_store(PERSONAL_MEMORY_COLLECTION)
    documents = [_memory_document(memory) for memory in memories]
    vector_store.add_texts(
        texts=[document.page_content for document in documents],
        metadatas=[document.metadata for document in documents],
        ids=[str(memory.id) for memory in memories],
    )


def _delete_memory_vector(memory_id: str) -> None:
    vector_store = create_vector_store(PERSONAL_MEMORY_COLLECTION)
    vector_store.delete(ids=[str(memory_id)])


def _load_memories_by_ids_in_order(db, user_id: str, memory_ids: list[str]):
    unique_ids = list(dict.fromkeys(memory_ids)) ## didn't use set because it didn't preserve the order of the ids
    memories = get_memories_by_ids(
        db=db,
        user_id=user_id,
        memory_ids=unique_ids,
    )
    memories_by_id = {str(memory.id): memory for memory in memories}
    return [
        memories_by_id[memory_id]
        for memory_id in unique_ids
        if memory_id in memories_by_id
    ]

def _semantic_memory_candidates(db, user_id: str, query: str):
    vector_store = create_vector_store(PERSONAL_MEMORY_COLLECTION)

    scored_docs = vector_store.similarity_search_with_score(
        query=query,
        k=1,
        filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=str(user_id)),
                )
            ]
        ),
    )

    if not scored_docs:
        return []

    doc, score = scored_docs[0]

    if score < settings.personal_memory_candidate_score_threshold:
        return []

    memory_id = doc.metadata.get("memory_id")
    if not memory_id:
        return []

    memory = get_memory_by_id(
        db=db,
        memory_id=memory_id,
    )

    if memory is None or memory.user_id != user_id or memory.is_deleted:
        return []

    return [(memory, score)]

def _reconcile_memory(existing_summary: str, incoming_memory: str, similarity_score: float):
    prompt = memory_reconciliation_prompt.format(
        existing_memory=existing_summary or "No existing memory.",
        incoming_memory=incoming_memory,
        similarity_score=f"{similarity_score:.4f}",
    )
    decision = memory_reconciliation_llm.invoke([HumanMessage(content=prompt)])
    # logger.info(
    #     "Memory Reconciled\nAction: %s\nConfidence: %.2f\nReason: %s",
    #     decision.action,
    #     decision.confidence,
    #     decision.reason,
    # )
    return decision


def _semantic_memory_search(db, user_id: str, query: str):
    vector_store = create_vector_store(PERSONAL_MEMORY_COLLECTION)
    docs = vector_store.similarity_search(
        query=query,
        k=PERSONAL_MEMORY_LIMIT,
        filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=str(user_id)),
                )
            ]
        ),
    )

    ranked_ids = []
    for doc in docs:
        memory_id = doc.metadata.get("memory_id")
        if not memory_id:
            continue

        ranked_ids.append(str(memory_id))

    return _load_memories_by_ids_in_order(
        db=db,
        user_id=user_id,
        memory_ids=ranked_ids,
    )


def store_user_memories(user_id: str, memories: list[str]):
    """Buffer and consolidate new memories into topic documents."""
    db = SessionLocal()
    try:
        vector_sync = []
        for memory in memories:
            normalized = _normalize_memory_text(memory)
            if not normalized:
                continue

            stored_memory = None
            try: 
                ## fetching existing related memory with the help of cosine similarity
                candidates = _semantic_memory_candidates(
                    db=db,
                    user_id=user_id,
                    query=normalized,
                )
            except Exception:
                logger.exception("Semantic personal memory dedupe failed")
                candidates = []

            candidate = None
            score = 0.0
            if candidates:
                candidate, score = candidates[0]

            try:
                decision = _reconcile_memory(
                    existing_summary=candidate.summary if candidate else "",
                    incoming_memory=normalized,
                    similarity_score=score,
                )
            except Exception:
                logger.exception("Memory reconciliation failed")
                continue

            action = decision.action
            next_summary = _normalize_memory_text(decision.updated_summary or "")

            if action == "ignore":
                continue

            if action == "delete":
                if candidate is None:
                    continue

                create_conflict(
                    db=db,
                    user_id=user_id,
                    topic_id=candidate.id,
                    conflict_type=action,
                    existing_summary=candidate.summary,
                    incoming_content=normalized,
                )
                deleted_memory = soft_delete_memory_summary(
                    db=db,
                    memory_id=candidate.id,
                )
                if deleted_memory is not None:
                    vector_sync.append(("delete", str(deleted_memory.id)))
                continue

            if action == "create" or candidate is None:
                summary = next_summary or normalized
                event = create_memory(
                    db=db,
                    user_id=user_id,
                    memory_text=summary,
                )
                if event is None:
                    continue

                stored_memory = get_memory_by_id(db=db, memory_id=event.topic_id)
            elif action in {"replace", "merge"}:
                if not next_summary:
                    logger.warning(
                        "Memory reconciliation returned %s without updated_summary",
                        action,
                    )
                    continue

                create_conflict(
                    db=db,
                    user_id=user_id,
                    topic_id=candidate.id,
                    conflict_type=action,
                    existing_summary=candidate.summary,
                    incoming_content=normalized,
                )
                stored_memory = update_memory_summary(
                    db=db,
                    memory_id=candidate.id,
                    memory_text=next_summary,
                    change_reason=f"memory_{action}",
                )
                if stored_memory is not None:
                    create_memory_event(
                        db=db,
                        user_id=user_id,
                        topic_id=stored_memory.id,
                        memory_text=normalized,
                    )
            else:
                logger.warning(
                    "Unsupported memory reconciliation action: %s",
                    action,
                )
                continue

            if stored_memory is not None:
                vector_sync.append(("upsert", stored_memory))

        db.commit()

        for operation, payload in vector_sync:
            try:
                if operation == "delete":
                    _delete_memory_vector(payload)
                else:
                    _index_memory(payload)
            except Exception:
                logger.exception("Failed to synchronize personal memory vector")
    except Exception:
        logger.exception("Failed to store user memories")
        db.rollback()
        raise
    finally:
        db.close()


def retrieve_user_memories(user_id: str, query: str | None = None):
    """Retrieve the most relevant topic documents for prompt construction."""
    db = SessionLocal()
    try:
        normalized_query = _normalize_memory_text(query or "")
        if normalized_query:
            try:
                semantic_memories = _semantic_memory_search(
                    db=db,
                    user_id=user_id,
                    query=normalized_query,
                )
                if semantic_memories:
                    return semantic_memories
            except Exception:
                logger.exception("Semantic personal memory retrieval failed")

        memories = get_memories_for_user(db=db, user_id=user_id)
        return memories[:PERSONAL_MEMORY_LIMIT]
    finally:
        db.close()


def index_user_memory_vectors(user_id: str) -> int:
    """One-time maintenance routine to backfill vectors for existing memories."""
    db = SessionLocal()
    try:
        memories = get_memories_for_user(db=db, user_id=user_id)
        _index_memories(memories)
        return len(memories)
    finally:
        db.close()


def consolidate_user_memories(user_id: str):
    """Convenience entry point for periodic consolidation maintenance."""
    return store_user_memories(user_id=user_id, memories=[])


def maintain_user_memory(user_id: str):
    """Trigger scheduled maintenance on the user's memory topics."""
    return consolidate_user_memories(user_id=user_id)

from collections.abc import Sequence
from langchain_core.documents import Document
from langsmith import traceable
from qdrant_client.http.models import Distance, VectorParams
from threadcore.infrastructure.vector.qdrant import client, create_vector_store


LONG_TERM_COLLECTION = "user_messages"


def _ensure_long_term_collection() -> None:
    if client.collection_exists(LONG_TERM_COLLECTION):
        return

    client.create_collection(
        collection_name=LONG_TERM_COLLECTION,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )


@traceable(name="Store User Messages")
def add_user_messages_to_vector_store(texts: Sequence[str], user_id: int):
    _ensure_long_term_collection()
    docs = [
        Document(
            page_content=text,
            metadata={"user_id": user_id},
        )
        for text in texts
    ]

    vector_store = create_vector_store(LONG_TERM_COLLECTION)
    vector_store.add_documents(docs)
    return vector_store


@traceable(name="Retrieve User Messages")
def retrieve_user_messages_from_vector_store(query: str, user_id: int):
    vector_store = create_vector_store(LONG_TERM_COLLECTION)
    retriever = vector_store.as_retriever(
        search_kwargs={
            "filter": {
                "must": [
                    {"key": "user_id", "match": {"value": user_id}},
                ]
            }
        }
    )
    return retriever.invoke(query)


from collections.abc import Sequence
from langchain_core.documents import Document
from langsmith import traceable
from qdrant_client.http.models import Distance, VectorParams
from threadcore.infrastructure.vector.qdrant import client, create_vector_store


CHAT_COLLECTION = "chat_embeddings"


def create_collection_if_not_exists(collection_name: str) -> None:
    if client.collection_exists(collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )


@traceable(name="Store Chat Embeddings")
def store_chat_embeddings(documents: Sequence[Document], user_id: int, thread_id: str):
    create_collection_if_not_exists(CHAT_COLLECTION)
    vector_store = create_vector_store(CHAT_COLLECTION)

    prepared_docs = []
    for document in documents:
        document.metadata.update(
            {
                "user_id": user_id,
                "thread_id": thread_id,
            }
        )
        prepared_docs.append(document)

    vector_store.add_documents(prepared_docs)
    return vector_store


@traceable(name="Retrieve Chat Embeddings")
def retrieve_chat_embeddings(query: str, user_id: int, thread_id: str):
    vector_store = create_vector_store(CHAT_COLLECTION)
    retriever = vector_store.as_retriever(
        search_kwargs={
            "filter": {
                "must": [
                    {"key": "user_id", "match": {"value": user_id}},
                    {"key": "thread_id", "match": {"value": thread_id}},
                ]
            }
        }
    )
    return retriever.invoke(query)


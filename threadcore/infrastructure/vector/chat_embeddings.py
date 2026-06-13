from collections.abc import Sequence
from langchain_core.documents import Document
from langsmith import traceable
from qdrant_client.http.models import Distance, VectorParams
from threadcore.infrastructure.vector.qdrant import client, create_vector_store


CHAT_COLLECTION = "CHAT_COLLECTION"


def create_collection_if_not_exists(collection_name: str) -> None:
    if client.collection_exists(collection_name):
        return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=3072, distance=Distance.COSINE),  
    )


@traceable(name="Store Chat Embeddings")
def store_chat_embeddings(
    documents: Sequence[Document],
    user_id: int,
    thread_id: str,
):
    print("=" * 50)
    print("STORE CHAT EMBEDDINGS STARTED")
    print(f"Documents received: {len(documents)}")
    print(f"User ID: {user_id}")
    print(f"Thread ID: {thread_id}")

    create_collection_if_not_exists(CHAT_COLLECTION)

    print("Collection checked/created")

    vector_store = create_vector_store(CHAT_COLLECTION)

    print("Vector store created")

    prepared_docs = []

    for i, document in enumerate(documents):
        document.metadata.update(
            {
                "user_id": user_id,
                "thread_id": thread_id,
            }
        )

        prepared_docs.append(document)

        if i < 3:
            print(f"\nDocument {i + 1}")
            print("Content:", document.page_content[:200])
            print("Metadata:", document.metadata)

    print(f"\nPrepared docs count: {len(prepared_docs)}")

    vector_store.add_documents(prepared_docs)

    print("Documents successfully added to Qdrant")
    print("=" * 50)

    return vector_store


@traceable(name="Retrieve Chat Embeddings")
def retrieve_chat_embeddings(query: str, user_id: str, thread_id: str):

    create_collection_if_not_exists(CHAT_COLLECTION)

    vector_store = create_vector_store(CHAT_COLLECTION)

    #  Filter by both user_id AND thread_id
    retriever = vector_store.as_retriever(
    search_kwargs={
        "filter": {
            "must": [
                {"key": "metadata.user_id", "match": {"value": user_id}},        # ← added metadata.
                {"key": "metadata.thread_id", "match": {"value": thread_id}},    # ← added metadata.
            ]
            }
        }
    )

    result = retriever.invoke(query)

    print(f"Retrieved docs: {len(result)}")

    for i, doc in enumerate(result):
        print(f"\nRetrieved Doc {i+1}")
        print(doc.page_content[:200])
        print(doc.metadata)

    print("=" * 50)

    return result
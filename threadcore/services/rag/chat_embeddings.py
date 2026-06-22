from collections.abc import Sequence

from langchain_core.documents import Document
from langsmith import traceable
from qdrant_client.models import Filter, FieldCondition, MatchValue

from threadcore.infrastructure.vector.qdrant import (
    client,
    create_vector_store,
)

CHAT_COLLECTION = "CHAT_COLLECTIONN"


@traceable(name="Store Chat Embeddings")
def store_chat_embeddings(
    documents: Sequence[Document],
    user_id: str,
    thread_id: str,
):
    print("=" * 50)
    print("STORE CHAT EMBEDDINGS STARTED")
    print(f"Documents received: {len(documents)}")
    print(f"User ID: {user_id}")
    print(f"Thread ID: {thread_id}")

    vector_store = create_vector_store(CHAT_COLLECTION)

    prepared_docs = []

    for document in documents:
        document.metadata.update(
            {
                "user_id": str(user_id),
                "thread_id": str(thread_id),
            }
        )
        prepared_docs.append(document)

    vector_store.add_documents(prepared_docs)

    print("Documents stored successfully")

    # DEBUG
    collection_info = client.get_collection(CHAT_COLLECTION)
    print("Total points:", collection_info.points_count)

    records, _ = client.scroll(
        collection_name=CHAT_COLLECTION,
        limit=3,
        with_payload=True,
        with_vectors=False,
    )

    print("\nSAMPLE PAYLOADS:")
    for record in records:
        print(record.payload)

    print("=" * 50)

    return vector_store





from qdrant_client.models import Filter, FieldCondition, MatchValue


@traceable(name="Retrieve Chat Embeddings")
def retrieve_chat_embeddings(
    query: str,
    user_id: str,
    thread_id: str,
):
    print("=" * 50)
    print("RETRIEVAL STARTED")
    print("COLLECTION:", CHAT_COLLECTION)
    print("Query:", query)
    print("User ID:", user_id)
    print("Thread ID:", thread_id)
    print("\n\n")
    print("=" * 80)
    print("DEBUG FILE LOADED")
    print(__file__)
    print("=" * 80)

    print("RETRIEVAL STARTED")
    print("COLLECTION:", CHAT_COLLECTION)
    print("Query:", query)
    print("User ID:", user_id)
    print("Thread ID:", thread_id)

    # --------------------------------------------------
    # COLLECTION INFO
    # --------------------------------------------------
    collection = client.get_collection(CHAT_COLLECTION)

    print("\nCOLLECTION INFO")
    print("Points:", collection.points_count)
    print("Config:", collection.config)

    # --------------------------------------------------
    # EMBEDDING TEST
    # --------------------------------------------------
    vector_store = create_vector_store(CHAT_COLLECTION)

    test_embedding = vector_store.embeddings.embed_query("hello")

    print("\nEMBEDDING INFO")
    print("Embedding length:", len(test_embedding))

    # --------------------------------------------------
    # DIRECT FILTER TEST
    # --------------------------------------------------
    records, _ = client.scroll(
        collection_name=CHAT_COLLECTION,
        limit=100,
        with_payload=True,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.user_id",
                    match=MatchValue(value=str(user_id)),
                ),
                FieldCondition(
                    key="metadata.thread_id",
                    match=MatchValue(value=str(thread_id)),
                ),
            ]
        ),
    )

    print(f"\nDIRECT FILTER MATCHES: {len(records)}")

    for i, record in enumerate(records[:3]):
        print(f"\nMatch {i + 1}")
        print(record.payload)

    # --------------------------------------------------
    # RAW SIMILARITY SEARCH
    # --------------------------------------------------
    try:
        docs = vector_store.similarity_search(
            query=query,
            k=5,
        )

        print(f"\nSIMILARITY SEARCH DOCS: {len(docs)}")

        for i, doc in enumerate(docs):
            print(f"\nSimilarity Doc {i+1}")
            print(doc.page_content[:200])
            print(doc.metadata)

    except Exception as e:
        print("\nSIMILARITY SEARCH ERROR")
        print(e)

    # --------------------------------------------------
    # FILTERED RETRIEVER
    # --------------------------------------------------
    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": Filter(
                must=[
                    FieldCondition(
                        key="metadata.user_id",
                        match=MatchValue(value=str(user_id)),
                    ),
                    FieldCondition(
                        key="metadata.thread_id",
                        match=MatchValue(value=str(thread_id)),
                    ),
                ]
            ),
        }
    )

    result = retriever.invoke(query)

    print(f"\nRETRIEVER DOCS: {len(result)}")

    for i, doc in enumerate(result):
        print(f"\nRetriever Doc {i + 1}")
        print(doc.page_content[:200])
        print(doc.metadata)

    print("=" * 50)

    return result   

from collections.abc import Sequence
from langchain_core.documents import Document
from langsmith import traceable
from qdrant_client.models import Filter, FieldCondition, MatchValue
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

    collection_info = client.get_collection(CHAT_COLLECTION)

    records, _ = client.scroll(
        collection_name=CHAT_COLLECTION,
        limit=3,
        with_payload=True,
        with_vectors=False,
    )
    return vector_store

@traceable(name="Retrieve Chat Embeddings")
def retrieve_chat_embeddings(
    query: str,
    user_id: str,
    thread_id: str,
):

    # COLLECTION 
    collection = client.get_collection(CHAT_COLLECTION)

    # EMBEDDING 
    vector_store = create_vector_store(CHAT_COLLECTION)

    test_embedding = vector_store.embeddings.embed_query("hello")

    # DIRECT FILTER 
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

    try:
        docs = vector_store.similarity_search(
            query=query,
            k=5,
        )

    except Exception as e:
        print(e)

    # FILTERED RETRIEVER
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

    return result   

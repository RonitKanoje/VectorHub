from qdrant_client.http.models import VectorParams, Distance
from qdrant_client import QdrantClient
from langchain_core.documents import Document
from langsmith import traceable
from database.qdrant.vectorStore import create_vector_store,client


@traceable(name="Create Collection If Not Exists")
def create_collection_if_not_exists(collection_name, docs):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
    vectorstore = create_vector_store(collection_name)
    vectorstore.add_documents(docs)
    return vectorstore




def store_chat_embeddings(texts, user_id, thread_id):

    docs = [
        Document(
            page_content=text,
            metadata={
                "user_id": user_id,
                "thread_id": thread_id
            }
        )
        for text in texts
    ]

    return create_collection_if_not_exists("video_embeddings", docs)
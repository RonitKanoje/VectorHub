from qdrant_client.http.models import VectorParams, Distance
from qdrant_client import QdrantClient
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

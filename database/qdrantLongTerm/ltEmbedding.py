from qdrant_client.http.models import VectorParams, Distance
from qdrant_client import QdrantClient
from langsmith import traceable
from database.qdrantLongTerm.ltVectorStore import create_vector_store,client

@traceable(name="adding user messages to vector store")

def add_user_messages_to_vector_store(docs):

    vectorstore = create_vector_store("user_messages")
    vectorstore.add_documents(docs)
    return vectorstore

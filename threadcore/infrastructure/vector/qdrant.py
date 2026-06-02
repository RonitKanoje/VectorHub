from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from threadcore.core.config import settings


embeddings = OllamaEmbeddings(model=settings.ollama_embedding_model)
client = QdrantClient(url=settings.qdrant_url)


def create_vector_store(collection_name: str) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )


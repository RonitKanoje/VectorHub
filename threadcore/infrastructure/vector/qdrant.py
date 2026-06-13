from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from threadcore.core.config import settings


embeddings = GoogleGenerativeAIEmbeddings(
    model=settings.gemini_embedding_model,
    google_api_key=settings.gemini_api_key,
)
client = QdrantClient(url=settings.qdrant_url)


def create_vector_store(collection_name: str) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )
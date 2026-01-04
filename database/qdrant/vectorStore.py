from langchain_community.embeddings import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

embeddings = OllamaEmbeddings(
    model= "bge-m3"
)

# Initialize Qdrant client and vector store
client = QdrantClient(url="http://localhost:6333")

def create_vector_store(collection_name: str) -> QdrantVectorStore:
    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings
    )    
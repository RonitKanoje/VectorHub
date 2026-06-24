from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import (
    QdrantVectorStore,
    FastEmbedSparse,
    RetrievalMode,
)
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    VectorParams,
    Distance,
    SparseVectorParams,
    Modifier,
)
from threadcore.core.config import settings


embeddings = OllamaEmbeddings(
    model=settings.ollama_embedding_model,
    base_url=settings.ollama_base_url,
)

client = QdrantClient(url=settings.qdrant_url)


def create_vector_store(collection_name: str) -> QdrantVectorStore:
    try:
        exists = client.collection_exists(collection_name)

        if not exists:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1024,
                    distance=Distance.COSINE,
                ),
                sparse_vectors_config={
                    "langchain-sparse": SparseVectorParams(
                        modifier=Modifier.IDF
                    )
                },
            )

        sparse_embeddings = FastEmbedSparse(
            model_name="Qdrant/bm25"
        )

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
        )

    except ImportError:
        exists = client.collection_exists(collection_name)

        if not exists:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1024,
                    distance=Distance.COSINE,
                ),
            )

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
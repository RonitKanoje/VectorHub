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
from threadcore.services.rag.gemini_embeddings import GeminiEmbeddingsAdapter


embeddings = GeminiEmbeddingsAdapter(model_name="gemini-embedding-001")
client = QdrantClient(url=settings.qdrant_url)


def _get_embedding_dimension() -> int:
    return embeddings.dimension


def _ensure_collection(collection_name: str) -> None:
    exists = client.collection_exists(collection_name)
    expected_size = _get_embedding_dimension()

    if exists:
        info = client.get_collection(collection_name)
        if getattr(info.config.params, "vectors", None) is None:
            return
        current_size = info.config.params.vectors.get("size")
        if current_size != expected_size:
            client.delete_collection(collection_name)
            exists = False

    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=expected_size,
                distance=Distance.COSINE,
            ),
            sparse_vectors_config={
                "langchain-sparse": SparseVectorParams(modifier=Modifier.IDF)
            },
        )


def create_vector_store(collection_name: str) -> QdrantVectorStore:
    try:
        _ensure_collection(collection_name)

        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
        )

    except ImportError:
        _ensure_collection(collection_name)

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
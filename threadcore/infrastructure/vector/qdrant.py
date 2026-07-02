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
    expected_size = _get_embedding_dimension()

    exists = client.collection_exists(collection_name)

    if exists:
        info = client.get_collection(collection_name)

        vectors = info.config.params.vectors

        if vectors is None:
            return

        # Handle both single-vector and named-vector collections
        if isinstance(vectors, VectorParams):
            current_size = vectors.size
        elif isinstance(vectors, dict):
            current_size = next(iter(vectors.values())).size
        else:
            current_size = None

        print(f"Collection: {collection_name}")
        print(f"Expected dimension: {expected_size}")
        print(f"Current dimension: {current_size}")

        if current_size != expected_size:
            print("Embedding dimension changed. Recreating collection...")
            client.delete_collection(collection_name)
            exists = False

    if not exists:
        print(f"Creating collection '{collection_name}' with dimension {expected_size}")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=expected_size,
                distance=Distance.COSINE,
            ),
            sparse_vectors_config={
                "langchain-sparse": SparseVectorParams(
                    modifier=Modifier.IDF
                )
            },
        )


def create_vector_store(collection_name: str) -> QdrantVectorStore:
    _ensure_collection(collection_name)

    try:
        sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
        )

    except ImportError:
        print("fastembed not installed. Falling back to dense retrieval.")

        return QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )
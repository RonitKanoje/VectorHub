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
_SPARSE_EMBEDDINGS_UNSET = object()
_sparse_embeddings = _SPARSE_EMBEDDINGS_UNSET
_vector_stores: dict[str, QdrantVectorStore] = {}


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
                "langchain-sparse": SparseVectorParams(
                    modifier=Modifier.IDF
                )
            },
        )


def _get_sparse_embeddings():
    global _sparse_embeddings

    if _sparse_embeddings is _SPARSE_EMBEDDINGS_UNSET:
        try:
            _sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        except ImportError:
            _sparse_embeddings = None

    return _sparse_embeddings


def create_vector_store(collection_name: str) -> QdrantVectorStore:
    cached_store = _vector_stores.get(collection_name)
    if cached_store is not None:
        return cached_store

    _ensure_collection(collection_name)

    sparse_embeddings = _get_sparse_embeddings()
    if sparse_embeddings is not None:
        try:
            vector_store = QdrantVectorStore(
                client=client,
                collection_name=collection_name,
                embedding=embeddings,
                sparse_embedding=sparse_embeddings,
                retrieval_mode=RetrievalMode.HYBRID,
            )
        except ImportError:
            vector_store = QdrantVectorStore(
                client=client,
                collection_name=collection_name,
                embedding=embeddings,
            )

    else:
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

    _vector_stores[collection_name] = vector_store
    return vector_store

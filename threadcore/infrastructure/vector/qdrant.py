from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from threadcore.core.config import settings
from langchain_qdrant import FastEmbedSparse, RetrievalMode
from qdrant_client.http.models import (VectorParams,Distance,SparseVectorParams,Modifier)


embeddings = OllamaEmbeddings(
    model=settings.ollama_embedding_model,
    base_url=settings.ollama_base_url,
)

client = QdrantClient(url=settings.qdrant_url)


def create_vector_store(collection_name: str) -> QdrantVectorStore:

    try:
        
        exists = client.collection_exists(collection_name)

        collection_needs_creation = False

        if exists:
            try:
                existing = client.get_collection(collection_name)
                has_sparse = (
                    hasattr(existing.config.params, "sparse_vectors")
                    and existing.config.params.sparse_vectors is not None
                )

                if not has_sparse:
                    client.delete_collection(collection_name)
                    collection_needs_creation = True

            except Exception as e:
                try:
                    client.delete_collection(collection_name)
                except Exception:
                    pass

                collection_needs_creation = True

        else:
            collection_needs_creation = True

        if collection_needs_creation:

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

        collection_info = client.get_collection(collection_name)

        sparse_embeddings = FastEmbedSparse(
            model_name="Qdrant/bm25"
        )

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
            sparse_embedding=sparse_embeddings,
            retrieval_mode=RetrievalMode.HYBRID,
        )

        return vector_store

    except ImportError as e:

        from qdrant_client.http.models import (
            VectorParams,
            Distance,
        )

        exists = client.collection_exists(collection_name)

        if not exists:
            print("Creating dense collection...")

            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1024,
                    distance=Distance.COSINE,
                ),
            )

        collection_info = client.get_collection(collection_name)

        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
            embedding=embeddings,
        )

        return vector_store
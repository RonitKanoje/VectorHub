from qdrant_client.http.models import VectorParams,Distance
from backend.vectorStore import qdrantVecSt,COLLECTION_NAME
from qdrant_client import QdrantClient


def collection_has_vectors(client: QdrantClient, collection_name: str) -> bool:
    info = client.get_collection(collection_name)
    return info.points_count > 0

def create_collection_if_not_exists(client: QdrantClient, collection_name: str,docs : list):

    if not client.collection_exists(collection_name=collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE
            )
        )
        qdrantVecSt.add_documents(docs)

    else:
        if not collection_has_vectors(client, collection_name):
            qdrantVecSt.add_documents(docs)
        else:
            print("Embedding already exists in the collection.")

    return qdrantVecSt


def retrieveEmbed(text,qdrantVecSt=qdrantVecSt):
    retrieval = qdrantVecSt.as_retriever()
    result = retrieval.invoke(text)
    return result 

if __name__ == '__main__':
    pass
from langchain_community.embeddings import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams,Distance

embeddings = OllamaEmbeddings(
    model= "bge-m3"
)

client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "myCollection"

if not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=1024,
            distance=Distance.COSINE
        )
    )


qdrantVecSt = QdrantVectorStore(
    client = client,
    collection_name = COLLECTION_NAME,
    embedding=embeddings
)

def addDoc(docs,qdarantVecSt=qdrantVecSt):
    qdrantVecSt.add_documents(docs)
    return


def retriveEmbed(text,qdarantVecSt=qdrantVecSt):
    retrieval = qdrantVecSt.as_retriever()
    result = retrieval.invoke(text)
    return result 

if __name__ == '__main__':
    pass
from langchain_community.embeddings import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams,Distance

embeddings = OllamaEmbeddings(
    model= "bge-m3"
)

client = QdrantClient(url="http://localhost:6333")

client.create_collection(
    collection_name="myCollection",
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE
    )
)

qdrantVecSt = QdrantVectorStore.from_documents(
    client = client,
    collection_name = "myCollection",
    embedding=embeddings
)

def addDoc(docs):
    qdrantVecSt.add_documents(docs)
    return


def retriveEmbed(text):
    retrieval = qdrantVecSt.as_retriever()
    result = retrieval.invoke(text)
    return result 

if __name__ == '__main__':
    pass
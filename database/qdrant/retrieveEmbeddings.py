from langsmith import traceable
from database.qdrant.vectorStore import create_vector_store



@traceable(name="Retrieve Embeddings")
def retrieveEmbed(collection_name: str, text: str):
    vectorstore = create_vector_store(collection_name)
    return vectorstore.as_retriever().invoke(text)
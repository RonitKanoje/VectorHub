from langsmith import traceable
from database.qdrantLongTerm.ltVectorStore import add_user_messages_to_vector_store


@traceable(name = "retrieving user messages from vector store")
def retrieve_user_messages_from_vector_store(text):
    vectorstore = add_user_messages_to_vector_store()
    return vectorstore.as_retriever().invoke(text)
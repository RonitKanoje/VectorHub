from langchain.schema import Document
from langsmith import traceable
from database.qdrant.vectorStore import create_vector_store

@traceable(name="adding user messages to vector store")
def add_user_messages_to_vector_store(texts, user_id):

    docs = [
        Document(
            page_content=text,
            metadata={"user_id": user_id}
        )
        for text in texts
    ]

    vectorstore = create_vector_store("user_messages")
    vectorstore.add_documents(docs)

    return vectorstore
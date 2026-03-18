from langsmith import traceable
from database.qdrant.vectorStore import create_vector_store

@traceable(name="retrieving user messages from vector store")
def retrieve_user_messages_from_vector_store(text, user_id):
    vectorstore = create_vector_store("user_messages")

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "filter": {
                "must": [
                    {"key": "user_id", "match": {"value": user_id}}
                ]
            }
        }
    )

    return retriever.invoke(text)
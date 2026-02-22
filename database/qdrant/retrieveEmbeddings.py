from langsmith import traceable
from database.qdrant.vectorStore import create_vector_store



@traceable(name="Retrieve Embeddings")
def retrieveEmbed(text: str, user_id: str, thread_id: str):
    vectorstore = create_vector_store("video_embeddings")

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "filter": {
                "must": [
                    {"key": "user_id", "match": {"value": user_id}},
                    {"key": "thread_id", "match": {"value": thread_id}}
                ]
            }
        }
    )

    return retriever.invoke(text)
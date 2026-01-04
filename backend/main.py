from backend.ytBackend.app import ytt_vid
from backend.processing_chunks import convDoc
from backend.videobackend.process_video import addToChunk, vidToAud
from backend.status import redis_client
from langsmith import traceable
from database.qdrant.embeddingsStore import create_collection_if_not_exists
from database.qdrant.vectorStore import create_vector_store
import json
from database.qdrant.retrieveEmbeddings import retrieveEmbed

@traceable(name="Main Processing")
def main(path, media, thread_id):
    try:
        redis_client.set(thread_id, "processing")

        if media == "youtube":
            chunks = ytt_vid(path)
        elif media == "audio":
            chunks = addToChunk(path)
        elif media == "text":
            processChunks = convDoc(path)
        elif media == "video":
            aud = vidToAud(path)
            chunks = addToChunk(aud)

        if media != "text":
            processChunks = convDoc(chunks)

        redis_client.set(thread_id, "creating_embeddings")
        collection_name = thread_id
        vectorStore = create_collection_if_not_exists(collection_name, processChunks)   


        redis_client.set(thread_id, "completed")

    except Exception as e:
        redis_client.set(thread_id, f"failed: {str(e)}")
        print("Background Error:", e)


# @traceable(name = "Retrieve Answer")
# def retrieve_answer(query):
#     result = retrieveEmbed(query,qdrantVecSt)
#     return result
@traceable(name="Retrieve Answer")
def retrieve_answer(query, thread_id):
    answer = retrieveEmbed(thread_id, query)
    return answer


if __name__ == "__main__":
    main("vMGRbgXUEBQ","Where company database is discussed in this viseo")
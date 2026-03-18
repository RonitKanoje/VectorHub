from backend.ytBackend.app import ytt_vid
from backend.processing_chunks import convDoc,txtChunkDoc
from backend.videobackend.process_video import addToChunk, vidToAud
from backend.textbackend.app import split
from backend.status import redis_client
from langsmith import traceable
from database.qdrant.embeddingsStore import create_collection_if_not_exists
from database.qdrant.vectorStore import create_vector_store
import json
import os 
from database.qdrant.retrieveEmbeddings import retrieveEmbed
from database.qdrantLongTerm.ltRetrieveEmbeddings import retrieve_user_messages_from_vector_store

@traceable(name="Main Processing")
def main(path, media, thread_id, language=None):
    try:
        redis_client.set(thread_id, "processing")

        if media == "youtube":
            chunks = ytt_vid(path)
        elif media == "audio":
    
            # Build output path with proper separators
            output_dir = os.path.join("backend", "videobackend", "tmp", "audios")
            output_path = os.path.join(output_dir, f"{thread_id}.mp3")
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            chunks = addToChunk(output_path,language)
        elif media == "text":
            chunks = split(path)
            processChunks = txtChunkDoc(chunks)



        elif media == "video":
            aud = vidToAud(path,thread_id)
            chunks = addToChunk(aud, language)


        if media != "text":
            processChunks = convDoc(chunks)

        redis_client.set(thread_id, "creating_embeddings")
        print("TYPE:", type(chunks))
        for i, chunk in enumerate(processChunks):
            print(f"\n--- CHUNK {i} ---")
            print(repr(chunk))

        for doc in processChunks:
            doc.metadata["thread_id"] = thread_id
            doc.metadata["user_id"] = user_id   # VERY IMPORTANT
            doc.metadata["media_type"] = media
        vectorStore = create_collection_if_not_exists("video_embeddings", processChunks)   


        redis_client.set(thread_id, "completed")

    except Exception as e:
        redis_client.set(thread_id, f"failed: {str(e)}")
        print("Background Error:", e)


# @traceable(name = "Retrieve Answer")
# def retrieve_answer(query):
#     result = retrieveEmbed(query,qdrantVecSt)
#     return result
@traceable(name="Retrieve Answer")
def retrieve_answer(query, user_id, thread_id):
    answer = retrieveEmbed(query, user_id, thread_id)
    return answer

@traceable(name = "long term Retrieve Answer")
def long_term_retrieve_answer(query, thread_id):
    answer = retrieve_user_messages_from_vector_store(query)
    return answer


if __name__ == "__main__":
    main("vMGRbgXUEBQ","Where company database is discussed in this viseo")
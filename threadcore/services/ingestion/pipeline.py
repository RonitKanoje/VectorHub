from langsmith import traceable

from threadcore.infrastructure.cache.redis_client import redis_client
from threadcore.infrastructure.vector.chat_embeddings import store_chat_embeddings
from threadcore.infrastructure.vector.chat_embeddings import retrieve_chat_embeddings
from threadcore.infrastructure.vector.long_term_memory import (
    retrieve_user_messages_from_vector_store,
)
from threadcore.services.ingestion.chunking import (
    documents_from_text_chunks,
    documents_from_transcript,
)
from threadcore.services.media.text import split_text
from threadcore.services.media.video import extract_audio, transcribe_audio_to_chunks
from threadcore.services.media.youtube import fetch_transcript


@traceable(name="Main Processing")
def process_media_upload(
    path: str,
    media: str,
    thread_id: str,
    user_id: int,
    language: str | None = None,
):
    try:
        redis_client.set(thread_id, "processing")

        if media == "youtube":
            transcript_chunks = fetch_transcript(path)
            documents = documents_from_transcript(transcript_chunks)
        elif media == "audio":
            transcript_chunks = transcribe_audio_to_chunks(path, language)
            documents = documents_from_transcript(transcript_chunks)
        elif media == "video":
            audio_path = extract_audio(path, thread_id)
            transcript_chunks = transcribe_audio_to_chunks(audio_path, language)
            documents = documents_from_transcript(transcript_chunks)
        elif media == "text":
            text_chunks = split_text(path)
            documents = documents_from_text_chunks(text_chunks)
        else:
            raise ValueError(f"Unsupported media type: {media}")

        for document in documents:
            document.metadata["media_type"] = media

        store_chat_embeddings(documents, user_id=user_id, thread_id=thread_id)
        redis_client.set(thread_id, "completed")
    except Exception as exc:
        redis_client.set(thread_id, f"failed: {exc}")
        raise


@traceable(name="Retrieve Answer")
def retrieve_answer(query: str, user_id: int, thread_id: str):
    return retrieve_chat_embeddings(query, user_id=user_id, thread_id=thread_id)


@traceable(name="Long Term Retrieve Answer")
def long_term_retrieve_answer(query: str, user_id: int):
    return retrieve_user_messages_from_vector_store(query, user_id=user_id)

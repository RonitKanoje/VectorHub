from langsmith import traceable
from threadcore.infrastructure.cache.redis_client import set_thread_status
from threadcore.services.rag.chat_embeddings import store_chat_embeddings
from threadcore.services.rag.chat_embeddings import retrieve_chat_embeddings
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
        print("pipelineee")
        set_thread_status(thread_id, "processing")

        if media == "youtube":
            print("yt pipelineee")
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
        elif media == "pdf" or media == "document":
            from threadcore.services.media.pdf import parse_pdf
            from threadcore.services.ingestion.chunking import documents_from_semantic_text
            pdf_text = parse_pdf(path)
            documents = documents_from_semantic_text(pdf_text)
        else:
            raise ValueError(f"Unsupported media type: {media}")

        for document in documents:
            document.metadata["media_type"] = media

        store_chat_embeddings(documents, user_id=user_id, thread_id=thread_id)
        set_thread_status(thread_id, "completed")
    except Exception as exc:
        set_thread_status(thread_id, f"failed: {exc}")
        raise


@traceable(name="Retrieve Answer")
def retrieve_answer(query: str, user_id: int, thread_id: str):
    return retrieve_chat_embeddings(query, user_id=user_id, thread_id=thread_id)


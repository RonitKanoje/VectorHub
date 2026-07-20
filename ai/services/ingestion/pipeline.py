import os
import uuid
import json
import urllib.request

from langsmith import traceable
from ai.infrastructure.cache.redis_client import set_thread_status
from ai.services.rag.chat_embeddings import store_chat_embeddings
from ai.services.rag.chat_embeddings import retrieve_chat_embeddings
from ai.services.ingestion.chunking import (
    documents_from_text_chunks,
    documents_from_transcript,
)
from ai.services.media.text import split_text
from ai.services.media.video import extract_audio, transcribe_audio_to_chunks
from ai.services.media.youtube import fetch_transcript
from ai.services.media.pdf import parse_pdf
from ai.services.ingestion.chunking import documents_from_semantic_text


def get_youtube_title(video_id: str) -> str:
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        with urllib.request.urlopen(oembed_url) as response:
            data = json.loads(response.read().decode())
            return data.get("title", "YouTube Video")
    except Exception:
        return "YouTube Video"


@traceable(name="Main Processing")
def process_media_upload(
    path: str,
    media: str,
    thread_id: str,
    user_id: int,
    language: str | None = None,
    document_name: str | None = None,
):
    try:
        set_thread_status(thread_id, "processing")

        if media == "youtube":
            transcript_chunks = fetch_transcript(path)
            documents = documents_from_transcript(transcript_chunks)
            if not document_name:
                document_name = get_youtube_title(path)
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
            if not document_name:
                document_name = "Untitled Text"
        elif media == "pdf" or media == "document":
            pdf_text = parse_pdf(path)
            documents = documents_from_semantic_text(pdf_text)
        else:
            raise ValueError(f"Unsupported media type: {media}")

        if not document_name:
            document_name = os.path.basename(path)

        document_id = str(uuid.uuid4())

        for document in documents:
            document.metadata["document_id"] = document_id
            document.metadata["document_name"] = document_name
            document.metadata["media_type"] = media

        store_chat_embeddings(documents, user_id=user_id, thread_id=thread_id)
        set_thread_status(thread_id, "completed")
    except Exception as exc:
        set_thread_status(thread_id, f"failed: {exc}")
        raise


@traceable(name="Retrieve Answer")
def retrieve_answer(query: str, user_id: int, thread_id: str):
    return retrieve_chat_embeddings(query, user_id=user_id, thread_id=thread_id)


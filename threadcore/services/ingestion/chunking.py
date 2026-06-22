from langchain_core.documents import Document


def cluster_transcript_chunks(chunks, group_size: int = 7):
    clustered = []

    for index in range(0, len(chunks), group_size):
        batch = chunks[index : index + group_size]
        text = [chunk["text"] for chunk in batch]
        duration = sum(chunk.get("duration", 0) for chunk in batch)
        source = batch[0].get("video_id") or batch[0].get("source")

        clustered.append(
            {
                "source": source,
                "text": " ".join(text),
                "start": batch[0].get("start", 0),
                "duration": duration,
            }
        )

    return clustered


def documents_from_transcript(chunks):
    clustered_chunks = cluster_transcript_chunks(chunks)
    return [
        Document(
            page_content=chunk["text"],
            metadata={
                "source": chunk.get("source"),
                "start": chunk.get("start", 0),
                "duration": chunk.get("duration", 0),
            },
        )
        for chunk in clustered_chunks
    ]


def documents_from_text_chunks(chunks):
    if not chunks:
        raise ValueError("No text chunks were generated")

    documents = []
    offset = 0

    for chunk in chunks:
        cleaned = chunk.strip()
        if not cleaned:
            continue

        token_length = len(cleaned.split())
        documents.append(
            Document(
                page_content=cleaned,
                metadata={
                    "start": offset,
                    "duration": token_length,
                },
            )
        )
        offset += token_length

    if not documents:
        raise ValueError("No valid documents available after filtering")

    return documents

from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import Document as LlamaDocument
from threadcore.core.config import settings

def documents_from_semantic_text(text: str):
    embed_model = OllamaEmbedding(
        model_name=settings.ollama_embedding_model,
        base_url=settings.ollama_base_url,
    )
    splitter = SemanticSplitterNodeParser(
        buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
    )
    nodes = splitter.get_nodes_from_documents([LlamaDocument(text=text)])
    
    documents = []
    for node in nodes:
        documents.append(
            Document(
                page_content=node.get_content(),
                metadata={"type": "semantic_chunk"}
            )
        )
    return documents


from backend.ytBackend.app import ytt_vid
from backend.processing_chunks import convDoc
from backend.embeddings import retrieveEmbed,create_collection_if_not_exists,qdrantVecSt
from backend.videobackend.process_video import addToChunk,vidToAud

import json


def main(path,media,thread_id):
    if media == "youtube":
        chunks = ytt_vid(path)
    elif media == 'audio':
        chunks = addToChunk(path)
    elif media == 'text':
        processChunks = convDoc(path)
    elif media == 'video':
        aud = vidToAud(path)
        chunks = addToChunk(aud)
    if media != "text" :
        processChunks = convDoc(chunks)
    create_collection_if_not_exists(qdrantVecSt.client, f"{thread_id}", processChunks)
    return 

def retrieve_answer(query):
    result = retrieveEmbed(query,qdrantVecSt)
    return result

if __name__ == "__main__":
    main("vMGRbgXUEBQ","Where company database is discussed in this viseo")
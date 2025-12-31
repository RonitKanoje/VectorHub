from backend.ytBackend.app import ytt_vid
from backend.processing_chunks import convDoc
from backend.embeddings import addDoc,retriveEmbed,qdrantVecSt
import json


def main(text,query):
    chunks = ytt_vid(text)
    processChunks = convDoc(chunks)
    addDoc(processChunks,qdrantVecSt) #### this is time taking process
    result = retriveEmbed(query,qdrantVecSt)
    return result

if __name__ == "__main__":
    main("vMGRbgXUEBQ","Where company database is discussed in this viseo")
from langchain_core.documents import Document
from backend.ytBackend.app import ytt_vid
import json

def cluster(chunks, group_size=7):
    clustered = []

    for i in range(0, len(chunks), group_size):
        text = []
        duration = 0

        for chunk in chunks[i:i + group_size]:
            if "video_id" in chunk:
                video_id = chunk[video_id]
            else:
                video_id = None
            text.append(chunk["text"])
            duration += chunk["duration"]

        clustered.append({
            "video_id" : video_id,
            "text": " ".join(text),
            "start": chunks[i]["start"],
            "duration": duration
        })

    return clustered


def convDoc(oldChunks):
    chunks = cluster(oldChunks)
    docs = [Document(
        page_content = chunk['text'],
        metadata = {
            'start' : chunk['start'],
            'duration' : chunk['duration']
        }
    )
    for chunk in chunks]
    return docs

if __name__ == "__main__":
    with open("docs.json", "r") as f:
        oldChunks = json.load(f)

    docs = convDoc(oldChunks) 
    print(docs)
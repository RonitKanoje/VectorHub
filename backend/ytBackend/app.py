## Importing necessary libraries
from youtube_transcript_api import YouTubeTranscriptApi
import json

### fetching the transcript 
def transcript(video_id):
    ytt_api = YouTubeTranscriptApi()
    ## error handling
    try:
        fetched = ytt_api.fetch(video_id)
        return fetched
    except Exception as e:
        raise e

### do error handling here in future
def ytt_vid(video_id):
    trans = transcript(video_id)
    finalChunks = trans.to_raw_data()
    return finalChunks


if __name__ == "__main__":
    docs = ytt_vid("vMGRbgXUEBQ")

    with open("docs2.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

## Importing necessary libraries
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.schema import Documents
import json

### fetching the transcript of youtube video
def transcript(video_id):
    ytt_api = YouTubeTranscriptApi()
    ## error handling
    try:
        fetched = ytt_api.fetch(video_id)
        return fetched
    except Exception as e:
        return e

### Clustering the chunks with start and duration for the better result
def cluster(chunks):
    newChunks = []
    count = 0
    txt = ''
    start = 0
    dur = 0
    for el in chunks:
        if count == 10:
            newChunks.append({
                'text' : txt,
                'start' : start,
                'duration' : dur
            })
            txt = ''
            start = el['start']
            count = 0
            dur = 0
        txt += el['text']
        dur += el['duration']
        count += 1

    ##handling last chunk
    if count != 0:
        newChunks.append({
            'text' : txt,
            'start' : start,
            'duration' : dur
        })

    return newChunks

def ytt_vid(video_id):
    trans = transcript(video_id)
    finalChunks = cluster(trans.to_raw_data())
    return finalChunks

if __name__ == "__main__":
    vidChunks = ytt_vid("vMGRbgXUEBQ")
    with open('chunks.json','w') as f:
        json.dump(vidChunks,f,indent=4,ensure_ascii=False)
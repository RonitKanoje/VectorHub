from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(video_id: str):

    transcript_api = YouTubeTranscriptApi()
    transcript = transcript_api.fetch(video_id)
    return transcript.to_raw_data()
from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(video_id: str):
    print("Fetching transcript...")

    transcript_api = YouTubeTranscriptApi()

    transcript = transcript_api.fetch(video_id)

    print("Transcript fetched successfully")

    return transcript.to_raw_data()
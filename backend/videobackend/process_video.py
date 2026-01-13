import subprocess
import whisper
import torch
import json
import os
from langsmith import traceable

@traceable(name="Video to Audio Conversion")
def vidToAud(vidAdd, thread_id):
    # Normalize input path
    vidAdd = os.path.normpath(vidAdd)
    
    # Build output path with proper separators
    output_dir = os.path.join("backend", "videobackend", "tmp", "audios")
    output_path = os.path.join(output_dir, f"{thread_id}.mp3")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Verify input file exists
    if not os.path.exists(vidAdd):
        raise FileNotFoundError(f"Video file not found: {vidAdd}")
    
    # Run ffmpeg with error suppression for cleaner output
    try:
        subprocess.run(
            ["ffmpeg", "-i", vidAdd, output_path],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e.stderr}")
    
    return output_path

## Converting audio to chunks
@traceable(name="Audio to Chunks Conversion")
def addToChunk(audio_path: str, language: str = None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("large-v2", device=device)

    chunks = []

    # Transcribe ONE audio file
    result = model.transcribe(
        audio=audio_path,
        task="translate",
        language=language
    )

    # Single loop over segments
    for segment in result["segments"]:
        chunks.append({
            "video_no": audio_path,
            "text": segment["text"],
            "start": segment["start"],
            "duration": segment["end"] - segment["start"]
        })

    return chunks


if __name__ == "__main__":
    # vidToAud(
    #     r"F:\Projects\Major Project 2\backend\videobackend\SSYouTube.online_Basic Structure of an HTML Website  Sigma Web Development Course - Tutorial #3_144p.mp4"
    # )

    addToChunk("backend/videobackend/audios")

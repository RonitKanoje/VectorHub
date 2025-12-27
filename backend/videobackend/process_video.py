import os
import subprocess
import whisper
import torch
import json
import os

## converting video into audio
def vidToAud(vidAdd):
    os.makedirs("audios", exist_ok=True)  

    output_path = "backend/videoBackend/audios/output.mp3"
    subprocess.run(["ffmpeg", "-i", vidAdd, output_path],check=True)
    return

## Converting audio to chunks

def addToChunk(audioAdd):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(device)
    model = whisper.load_model("large-v2",device=device)
    chunks = []

    audios = os.listdir(audioAdd)
    print(audios)
    count = 1
    for audio in audios:
        result = model.transcribe(audio=f"backend/videobackend/audios/{audio}",language="hi",task = "translate")
        print(result)

    


if __name__ == "__main__":
    # vidToAud(
    #     r"F:\Projects\Major Project 2\backend\videobackend\SSYouTube.online_Basic Structure of an HTML Website  Sigma Web Development Course - Tutorial #3_144p.mp4"
    # )

    addToChunk("backend/videobackend/audios")

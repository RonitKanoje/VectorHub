import subprocess
import os
from pathlib import Path
from groq import Groq
from threadcore.core.config import settings


def extract_audio(video_path: str, thread_id: str) -> str:
    source_path = Path(video_path).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Video file not found: {source_path}")

    output_path = settings.audio_upload_dir / f"{thread_id}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "ffmpeg", "-i", str(source_path),
            "-ar", "16000",
            "-ac", "1",
            "-b:a", "32k",
            "-y",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )

    return str(output_path)


def transcribe_audio_to_chunks(audio_path: str, language: str | None = None):
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if file_size_mb > 50:
        raise ValueError(
            f"Audio file is {file_size_mb:.1f}MB — exceeds Groq's 25MB limit."
        )

    client = Groq(api_key=settings.groq_api_key)

    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3",
            response_format="verbose_json",
        )

    return [
    {
        "source": audio_path,
        "text": segment["text"],                        # ← dict access
        "start": segment["start"],
        "duration": segment["end"] - segment["start"],  # ← end - start
    }
    for segment in result.segments
]       
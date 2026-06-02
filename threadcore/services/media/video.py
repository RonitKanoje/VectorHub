import subprocess
from pathlib import Path
import torch
import whisper
from threadcore.core.config import settings


def extract_audio(video_path: str, thread_id: str) -> str:
    source_path = Path(video_path).resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Video file not found: {source_path}")

    output_path = settings.audio_upload_dir / f"{thread_id}.mp3"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["ffmpeg", "-i", str(source_path), str(output_path)],
        check=True,
    )

    return str(output_path)


def transcribe_audio_to_chunks(audio_path: str, language: str | None = None):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("large-v2", device=device)

    result = model.transcribe(
        audio=audio_path,
        task="translate",
        language=language,
    )

    return [
        {
            "source": audio_path,
            "text": segment["text"],
            "start": segment["start"],
            "duration": segment["end"] - segment["start"],
        }
        for segment in result["segments"]
    ]


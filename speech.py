import os
import shutil
from transformers import pipeline
import inspect


def transcribe_audio(audio_path: str, language_code: str) -> str:
    """Transcribe ``audio_path`` using Whisper with the given language code."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg não encontrado. Instale o pacote ffmpeg para processar arquivos de áudio."
        )

    asr = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3-turbo",
        token=os.getenv("HUGGINGFACE_TOKEN"),
    )

    call_params = inspect.signature(asr.__call__).parameters
    if "language" in call_params:
        result = asr(
            audio_path,
            language=language_code,
            return_timestamps=True,
        )
    else:
        result = asr(
            audio_path,
            return_timestamps=True,
            generate_kwargs={"language": language_code},
        )

    return result["text"].strip()

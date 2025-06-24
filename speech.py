import os
import shutil
from transformers import pipeline
from translator import LANG_CODE


def transcribe_audio(audio_path: str, language_name: str) -> str:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg não encontrado. Instale o pacote ffmpeg para processar arquivos de áudio.")
    lang_code = LANG_CODE.get(language_name, 'en')
    asr = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3-turbo",
        token=os.getenv("HUGGINGFACE_TOKEN"),
    )
    result = asr(audio_path, generate_kwargs={"language": lang_code})
    return result["text"].strip()

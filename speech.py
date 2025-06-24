import os
from transformers import pipeline
from translator import LANG_CODE


def transcribe_audio(audio_path: str, language_name: str) -> str:
    lang_code = LANG_CODE.get(language_name, 'en')
    asr = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-large-v3-turbo",
        token=os.getenv("HUGGINGFACE_TOKEN"),
    )
    result = asr(audio_path, generate_kwargs={"language": lang_code})
    return result["text"].strip()

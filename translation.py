import os
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import openai

# Mapping from Whisper language codes to NLLB codes used by the translation model
NLLB_CODES = {
    "portuguese": "por_Latn",
    "english": "eng_Latn",
    "spanish": "spa_Latn",
    "french": "fra_Latn",
}

# Language names for the OpenAI model
LANG_NAME = {
    "portuguese": "Portuguese",
    "english": "English",
    "spanish": "Spanish",
    "french": "French",
}

# Available translation models. The ``MODEL_NAME`` value can be switched at
# runtime using :func:`set_translation_model`.
MODEL_OPTIONS = {
    "1": "facebook/nllb-200-distilled-600M",
    "2": "gpt-3.5-turbo",
}

MODEL_NAME = MODEL_OPTIONS["1"]


def set_translation_model(option: str) -> None:
    """Set the translation model to one of ``MODEL_OPTIONS``.

    Parameters
    ----------
    option:
        The key corresponding to the desired model in ``MODEL_OPTIONS``.
    """
    global MODEL_NAME
    if option not in MODEL_OPTIONS:
        raise ValueError("Opção de modelo inválida")
    MODEL_NAME = MODEL_OPTIONS[option]
    _load_model.cache_clear()


def _get_openai_client():
    """Return OpenAI API client with API key loaded from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    openai.api_key = api_key
    return openai


@lru_cache(maxsize=1)
def _load_model():
    """Load and cache the translation model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    return tokenizer, model


def _chunk_text(text: str, size: int = 512) -> list[str]:
    """Split ``text`` into manageable chunks for translation."""
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_text(text: str, src_code: str, tgt_code: str) -> str:
    """Translate ``text`` from ``src_code`` to ``tgt_code`` using the selected model."""
    if src_code == tgt_code:
        return text

    if MODEL_NAME == "gpt-3.5-turbo":
        client = _get_openai_client()
        src_lang = LANG_NAME[src_code]
        tgt_lang = LANG_NAME[tgt_code]
        translations = []
        for chunk in _chunk_text(text, size=1500):
            response = client.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate from {src_lang} to {tgt_lang}.",
                    },
                    {"role": "user", "content": chunk},
                ],
                temperature=0,
            )
            translations.append(response.choices[0].message.content.strip())
        return " ".join(translations)

    tokenizer, model = _load_model()
    translator = pipeline(
        "translation",
        model=model,
        tokenizer=tokenizer,
        src_lang=NLLB_CODES[src_code],
        tgt_lang=NLLB_CODES[tgt_code],
        max_length=400,
    )

    translations = []
    for chunk in _chunk_text(text):
        result = translator(chunk)
        translations.append(result[0]["translation_text"].strip())

    return " ".join(translations)

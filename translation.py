from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Mapping from Whisper language codes to NLLB codes used by the translation model
NLLB_CODES = {
    "portuguese": "por_Latn",
    "english": "eng_Latn",
    "spanish": "spa_Latn",
    "french": "fra_Latn",
}

# Available translation models. The ``MODEL_NAME`` value can be switched at
# runtime using :func:`set_translation_model`.
MODEL_OPTIONS = {
    "1": "facebook/nllb-200-distilled-600M",
    "2": "openai/whisper-large-v3-turbo",
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

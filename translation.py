from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# Mapping from Whisper language codes to NLLB codes used by the translation model
NLLB_CODES = {
    "portuguese": "por_Latn",
    "english": "eng_Latn",
    "spanish": "spa_Latn",
    "french": "fra_Latn",
}

MODEL_NAME = "facebook/nllb-200-distilled-600M"


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
    """Translate ``text`` from ``src_code`` to ``tgt_code`` using NLLB."""
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

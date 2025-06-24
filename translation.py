import os
from functools import lru_cache
from transformers import pipeline



LANG_TOKEN = {
    "portuguese": "por_Latn",
    "english": "eng_Latn",
    "spanish": "spa_Latn",
    "french": "fra_Latn",
}


@lru_cache(maxsize=1)
def _get_translator():
    """Return a lazily loaded translation pipeline using NLLB."""
    return pipeline(
        "translation",
        model="facebook/nllb-200-distilled-600M",
        token=os.getenv("HUGGINGFACE_TOKEN"),
    )


def _chunk_text(text: str, size: int = 512) -> list[str]:
    """Split ``text`` into smaller chunks of approximately ``size`` characters."""
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_text(text: str, src_code: str, tgt_code: str) -> str:
    """Translate ``text`` from ``src_code`` to ``tgt_code`` using NLLB."""
    if src_code == tgt_code:
        return text

    translator = _get_translator()
    src_lang = LANG_TOKEN[src_code]
    tgt_lang = LANG_TOKEN[tgt_code]

    translations = []
    for chunk in _chunk_text(text):
        result = translator(
            chunk,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            max_length=512,
        )
        translations.append(result[0]["translation_text"])

    return " ".join(translations)

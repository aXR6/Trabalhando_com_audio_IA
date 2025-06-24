import os
from functools import lru_cache
from transformers import pipeline

from languages import NLLB_CODE


@lru_cache(maxsize=1)
def _get_translator():
    """Return a lazily loaded translation pipeline."""
    return pipeline(
        "translation",
        model="facebook/nllb-200-distilled-600M",
        token=os.getenv("HUGGINGFACE_TOKEN"),
    )


def translate_text(text: str, src_code: str, tgt_code: str) -> str:
    """Translate ``text`` from ``src_code`` to ``tgt_code`` using NLLB."""
    if src_code == tgt_code:
        return text

    translator = _get_translator()
    result = translator(
        text,
        src_lang=NLLB_CODE[src_code],
        tgt_lang=NLLB_CODE[tgt_code],
        max_length=400,
    )
    return result[0]["translation_text"]

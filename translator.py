from __future__ import annotations
import os
from functools import lru_cache
from transformers import pipeline

LANG_CODE = {
    'Português': 'por',
    'English': 'eng',
    'Español': 'spa',
    'Français': 'fra',
}

NLLB_LANG = {
    'por': 'por_Latn',
    'eng': 'eng_Latn',
    'spa': 'spa_Latn',
    'fra': 'fra_Latn',
}

@lru_cache(maxsize=1)
def _get_pipeline():
    """Return a lazy-loaded translation pipeline."""
    return pipeline(
        'translation',
        model='facebook/nllb-200-distilled-600M',
        token=os.getenv('HUGGINGFACE_TOKEN')
    )


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text between supported languages using an offline model."""
    src_code = NLLB_LANG[LANG_CODE[src_lang]]
    tgt_code = NLLB_LANG[LANG_CODE[tgt_lang]]

    translator = _get_pipeline()
    try:
        result = translator(text, src_lang=src_code, tgt_lang=tgt_code)
    except Exception as exc:  # pragma: no cover - runtime safety
        raise RuntimeError(f'Falha ao traduzir o texto: {exc}') from exc

    if not result:
        raise RuntimeError('Serviço de tradução retornou resultado vazio')

    return result[0]['translation_text']

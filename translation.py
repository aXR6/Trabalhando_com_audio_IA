import os
from functools import lru_cache
import openai



LANG_NAME = {
    "portuguese": "Portuguese",
    "english": "English",
    "spanish": "Spanish",
    "french": "French",
}


@lru_cache(maxsize=1)
def _get_client():
    """Return OpenAI API client with API key loaded from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    openai.api_key = api_key
    return openai


def _chunk_text(text: str, size: int = 1500) -> list[str]:
    """Split ``text`` into smaller chunks for the API limit."""
    return [text[i : i + size] for i in range(0, len(text), size)]


def translate_text(text: str, src_code: str, tgt_code: str) -> str:
    """Translate ``text`` from ``src_code`` to ``tgt_code`` using OpenAI."""
    if src_code == tgt_code:
        return text

    client = _get_client()
    src_lang = LANG_NAME[src_code]
    tgt_lang = LANG_NAME[tgt_code]

    translations = []
    for chunk in _chunk_text(text):
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

from transformers import pipeline

LANG_CODE = {
    'Português': 'pt',
    'English': 'en',
    'Español': 'es',
    'Français': 'fr',
}


def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    src_code = LANG_CODE[src_lang]
    tgt_code = LANG_CODE[tgt_lang]
    model_name = f"Helsinki-NLP/opus-mt-{src_code}-{tgt_code}"
    translator = pipeline('translation', model=model_name)
    result = translator(text, max_length=400)
    return result[0]['translation_text']

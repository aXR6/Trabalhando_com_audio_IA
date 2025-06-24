from googletrans import Translator

LANG_CODE = {
    'Português': 'pt',
    'English': 'en',
    'Español': 'es',
    'Français': 'fr',
}

def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    translator = Translator()
    src_code = LANG_CODE[src_lang]
    tgt_code = LANG_CODE[tgt_lang]
    result = translator.translate(text, src=src_code, dest=tgt_code)
    return result.text

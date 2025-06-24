from googletrans import Translator

LANG_CODE = {
    'Português': 'pt',
    'English': 'en',
    'Español': 'es',
    'Français': 'fr',
}

def translate_text(text: str, src_lang: str, tgt_lang: str) -> str:
    """Translate text between supported languages.

    Parameters
    ----------
    text: str
        The input text to translate.
    src_lang: str
        Human readable source language name.
    tgt_lang: str
        Human readable target language name.

    Returns
    -------
    str
        Translated text.

    Raises
    ------
    RuntimeError
        If the translation service fails to return a valid result.
    """

    # Using translate.googleapis.com directly avoids some parsing issues that
    # occur when hitting the default endpoint via googletrans.
    translator = Translator(service_urls=["translate.googleapis.com"])
    # googletrans 4.0.0-rc1 expects an attribute named ``raise_Exception`` in
    # ``Translator._translate`` but only ``raise_exception`` is defined. Add the
    # missing attribute for compatibility with this library version.
    if not hasattr(translator, "raise_Exception"):
        translator.raise_Exception = getattr(translator, "raise_exception", True)

    src_code = LANG_CODE[src_lang]
    tgt_code = LANG_CODE[tgt_lang]

    try:
        result = translator.translate(text, src=src_code, dest=tgt_code)
    except Exception as exc:
        raise RuntimeError(f"Falha ao traduzir o texto: {exc}") from exc

    if result is None or result.text is None:
        raise RuntimeError("Serviço de tradução retornou resultado vazio")

    return result.text

from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from dotenv import load_dotenv

from speech import transcribe_audio
from translation import translate_text
from languages import LANG_CODE
from db import init_db, save_record

load_dotenv()
console = Console()

LANG_OPTIONS = list(LANG_CODE.keys())


def choose_language(message: str) -> str:
    console.print(message)
    for idx, lang in enumerate(LANG_OPTIONS, 1):
        console.print(f"{idx}. {lang}")
    choice = IntPrompt.ask("Escolha", choices=[str(i) for i in range(1, len(LANG_OPTIONS)+1)])
    return LANG_OPTIONS[int(choice)-1]


def transcribe_menu():
    audio_path = Prompt.ask("Caminho do arquivo de áudio")
    src_lang = choose_language("Idioma de origem:")
    tgt_lang = choose_language("Traduzir para:")

    console.print("[bold]Transcrevendo...[/bold]")
    original_text = transcribe_audio(audio_path, LANG_CODE[src_lang])
    console.print("\n[bold]Texto extraído:[/bold]")
    console.print(original_text)

    console.print("\n[bold]Traduzindo...[/bold]")
    translated_text = translate_text(
        original_text,
        LANG_CODE[src_lang],
        LANG_CODE[tgt_lang],
    )
    console.print("\n[bold]Texto traduzido:[/bold]")
    console.print(translated_text)

    if Prompt.ask("Deseja salvar no banco de dados? (s/n)", choices=["s", "n"], default="n") == "s":
        user_name = Prompt.ask("Nome do usuário")
        subject = Prompt.ask("Assunto")
        save_record(user_name, subject, audio_path, original_text, translated_text)
        console.print("Registro salvo com sucesso.")


def main():
    init_db()
    while True:
        console.print("\n[bold]Menu[/bold]")
        console.print("1. Transcrever áudio")
        console.print("2. Sair")
        option = IntPrompt.ask("Escolha", choices=["1", "2"])
        if option == 1:
            transcribe_menu()
        else:
            break


if __name__ == "__main__":
    main()

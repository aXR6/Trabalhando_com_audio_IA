# Trabalhando com Audio IA

Este projeto demonstra o uso do modelo `openai/whisper-large-v3-turbo` da HuggingFace para transcrever arquivos de áudio e traduzir o texto para diferentes idiomas. Os resultados podem ser opcionalmente armazenados em um banco de dados PostgreSQL.

## Requisitos
- Python 3.10+
- PostgresSQL
- [FFmpeg](https://ffmpeg.org/)

## Configuração
1. Copie o arquivo `.env.example` para `.env` e ajuste as variáveis de ambiente.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   # FFmpeg é necessário para que o modelo leia arquivos de áudio.
   # Em sistemas Debian/Ubuntu, instale com:
   # sudo apt-get install ffmpeg

3. Crie a tabela no banco de dados executando o script `schema.sql`.

## Uso
Execute `python main.py` e navegue pelo menu para transcrever ou traduzir áudio ou texto.

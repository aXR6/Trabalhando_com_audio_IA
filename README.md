# Trabalhando com Audio IA

Este projeto demonstra o uso do modelo `openai/whisper-large-v3-turbo` da HuggingFace para transcrever arquivos de áudio. A tradução do texto é feita com o modelo `facebook/nllb-200-distilled-600M`. Os resultados podem ser opcionalmente armazenados em um banco de dados PostgreSQL.

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
Para utilizar no terminal, execute `python main.py` e navegue pelo menu para
transcrever arquivos de áudio.

Também é possível acessar as mesmas funcionalidades via navegador iniciando o
servidor web:

```bash
python web.py
```

Depois, abra `http://localhost:5000` para enviar o áudio pela interface
gráfica.

Ao abrir uma sessão existente, serão listados todos os áudios já processados,
incluindo o texto extraído e o texto traduzido. A página também informa os
modelos utilizados: `openai/whisper-large-v3-turbo` para transcrição e
`facebook/nllb-200-distilled-600M` para tradução.

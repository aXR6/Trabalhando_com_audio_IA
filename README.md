# Trabalhando com Áudio e IA

Este projeto demonstra como transcrever e traduzir arquivos de áudio utilizando modelos de inteligência artificial. São empregadas duas redes pré‑treinadas hospedadas no HuggingFace:

- **openai/whisper-large-v3-turbo** – responsável pela transcrição do áudio para texto.
- **facebook/nllb-200-distilled-600M** – usada para traduzir o texto para outros idiomas.

Os resultados podem opcionalmente ser salvos em um banco PostgreSQL, permitindo organizar sessões de transcrição e consultar registros anteriores por meio de uma interface web.

## Funcionalidades

- **Transcrição de áudio** em diferentes idiomas através do Whisper.
- **Tradução automática** do texto extraído para o idioma desejado.
- **Armazenamento opcional** dos resultados no banco de dados com registro de usuário, sessão e assunto.
- **Interface de linha de comando** simples para processar arquivos locais.
- **Aplicação web** em Flask com upload de múltiplos áudios, painel de sessões e visualização dos resultados.
- **Autenticação de usuários** com senha e PIN para recuperação de acesso.

## Requisitos

- Python 3.10+
- PostgreSQL configurado
- [FFmpeg](https://ffmpeg.org/) – necessário para que o Whisper consiga ler o áudio.

## Configuração

1. Copie o arquivo `.env.example` para `.env` e ajuste as variáveis de ambiente.
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
   Em sistemas Debian/Ubuntu, FFmpeg pode ser instalado com:
   ```bash
   sudo apt-get install ffmpeg
   ```
3. Crie as tabelas executando o script `schema.sql` no banco de dados.

## Usando pelo Terminal

Execute o script principal e siga as instruções exibidas:

```bash
python main.py
```

Você poderá escolher o idioma de origem, o idioma de destino e o arquivo de áudio a ser processado. Após a transcrição e tradução, o programa oferece a opção de salvar o resultado no banco de dados.

## Usando a Interface Web

Para utilizar pelo navegador, inicie o servidor Flask:

```bash
python web.py
```

Acesse `http://localhost:5000` para fazer login ou criar uma conta. Após entrar, escolha ou crie uma sessão. Dentro de cada sessão é possível fazer upload de um ou mais arquivos de áudio, definir os idiomas e opcionalmente salvar cada transcrição no banco de dados. O painel também lista todos os áudios já processados com seus textos originais e traduzidos.

## Executando com Docker e Nginx Unit

O projeto inclui um `Dockerfile` configurado para o [Nginx Unit](https://unit.nginx.org/). Para gerar a imagem execute:

```bash
docker build -t audio-app .
```

Depois crie o contêiner informando suas variáveis de ambiente (por exemplo o arquivo `.env`) e exponha a porta 8080:

```bash
docker run -d --env-file .env -p 8080:8000 audio-app
```

A interface web ficará acessível em `http://localhost:8080`.

## Estrutura do Banco de Dados

O banco utiliza três tabelas principais:

- `users` – guarda os usuários cadastrados junto com o hash da senha e o PIN de recuperação.
- `sessions` – registra as sessões associadas a cada usuário.
- `audio_records` – armazena os áudios processados, vinculados à sessão correspondente.

Dessa forma, um usuário pode ter diversas sessões, e cada sessão agrupa seus respectivos registros de áudio.

---

Este repositório fornece um ponto de partida simples para trabalhar com processamento de áudio assistido por IA. Sinta‑se à vontade para personalizar o código e expandir as funcionalidades conforme necessário.


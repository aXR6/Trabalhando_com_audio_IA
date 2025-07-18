#!/usr/bin/env bash

# clean_pycache.sh — remove pastas __pycache__ recursivamente
find . -type d -name "__pycache__" -exec rm -rf {} +

set -euo pipefail

# Nome do diretório do venv e do arquivo de requisitos
ENV_DIR=".venv"
REQ_FILE="requirements.txt"

# 1) Criar o venv, se necessário
if [ ! -d "$ENV_DIR" ]; then
  echo "🛠  Criando virtualenv em $ENV_DIR..."
  python3 -m venv "$ENV_DIR"
else
  echo "✔️  Virtualenv já existe em $ENV_DIR"
fi

# 2) Ativar o ambiente na sessão atual
echo "🚀  Ativando o virtualenv..."
# este comando só funciona se você fizer `source init-env.sh`
# em vez de `./init-env.sh`
source "$ENV_DIR/bin/activate"

# 3) Garantir pip/setuptools/wheel atualizados
echo "⬆️  Atualizando pip para versão estável..."
python3 -m pip install --upgrade "pip<25" setuptools wheel

# 4) Garantir ffmpeg instalado
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "📼  Instalando ffmpeg..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y ffmpeg
  else
    echo "⚠️  ffmpeg não encontrado e instalação automática indisponível. Instale manualmente."
  fi
else
  echo "✔️  ffmpeg já está instalado"
fi

# 5) Instalar todas as libs do requirements.txt
if [ -f "$REQ_FILE" ]; then
  echo "📦  Instalando dependências de $REQ_FILE..."
  pip install -r "$REQ_FILE"
else
  echo "⚠️  Arquivo $REQ_FILE não encontrado. Coloque seu requirements.txt na raiz do projeto."
  return 1 2>/dev/null || exit 1
fi

echo
echo "✅ Ambiente pronto! Você está usando:"
echo "   Python: $(python --version)"
echo "   Pip:    $(pip --version)"
echo
echo "Para sair do venv: deactivate"

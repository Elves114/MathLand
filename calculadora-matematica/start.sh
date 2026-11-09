#!/usr/bin/env bash
# MathLab — cria o ambiente virtual (se necessário) e arranca o servidor.
set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "A criar o ambiente virtual..."
  python3 -m venv .venv
fi

.venv/bin/pip install --quiet -r requirements.txt

echo "A arrancar o MathLab em http://127.0.0.1:5000  (Ctrl+C para parar)"
exec .venv/bin/python backend/app.py

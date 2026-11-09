@echo off
rem MathLab — cria o ambiente virtual (se necessario) e arranca o servidor no Windows.
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist .venv (
  echo A criar o ambiente virtual...
  python -m venv .venv 2>nul || py -m venv .venv
  if not exist .venv (
    echo.
    echo [ERRO] Nao foi possivel criar o ambiente virtual.
    echo        Instale o Python 3 e certifique-se de que esta no PATH.
    echo.
    pause
    exit /b 1
  )
)

.venv\Scripts\python -m pip install --quiet -r requirements.txt
if errorlevel 1 (
  echo [ERRO] Falha ao instalar as dependencias.
  pause
  exit /b 1
)

echo A arrancar o MathLab em http://127.0.0.1:5000  (Ctrl+C para parar)
.venv\Scripts\python backend\app.py

endlocal

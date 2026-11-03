@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Instala Python 3.12 desde https://www.python.org/downloads/ y vuelve a abrir este archivo.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  py -3.12 -m venv .venv
  if errorlevel 1 goto error
)
if not exist ".venv\nexplay_instalado" (
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 goto error
  echo listo>".venv\nexplay_instalado"
)
start "NexPlay" http://localhost:8501
".venv\Scripts\python.exe" -m streamlit run app.py --server.address localhost
exit /b
:error
echo No se pudo preparar NexPlay. Revisa el mensaje anterior y tu conexion a Internet.
pause
exit /b 1

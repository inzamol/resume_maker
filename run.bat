@echo off
title AI Resume Architect & ATS Tailor
echo ===================================================
echo     Launching AI Resume Architect ^& ATS Tailor
echo ===================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [!] Virtual environment not detected. Creating .venv...
    python -m venv .venv
    echo [*] Installing dependencies...
    .venv\Scripts\pip.exe install -r requirements.txt
)

echo [*] Starting web application on http://localhost:8000
echo [*] Press Ctrl+C in this terminal to stop the server.
echo.

start http://localhost:8000

.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause


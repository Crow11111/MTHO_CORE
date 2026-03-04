@echo off
echo === ATLAS Wake Word Recorder ===
echo Stelle sicher, dass dein Mikrofon aktiv ist.
echo.

if not exist .venv (
    echo Venv nicht gefunden! Bitte erst '1_SETUP.bat' ausfuehren.
    pause
    exit /b
)

call .venv\Scripts\activate.bat
python scripts/record_clips.py
pause

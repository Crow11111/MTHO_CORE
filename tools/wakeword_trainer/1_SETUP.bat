@echo off
echo === ATLAS Wake Word Trainer Setup ===
echo.
echo 1. Pruefe Python Installation...
python --version
if errorlevel 1 (
    echo Python nicht gefunden! Bitte Python installieren und zum PATH hinzufuegen.
    pause
    exit /b
)

echo.
echo 2. Erstelle Virtual Environment (.venv)...
if not exist .venv (
    python -m venv .venv
    echo Venv erstellt.
) else (
    echo Venv existiert bereits.
)

echo.
echo 3. Installiere Abhaengigkeiten (kann dauern)...
call .venv\Scripts\activate.bat
pip install --upgrade pip
pip install openwakeword sounddevice soundfile numpy scipy scikit-learn onnxruntime
if errorlevel 1 (
    echo Fehler bei der Installation! Bitte Internetverbindung pruefen.
    pause
    exit /b
)

echo.
echo === SETUP ERFOLGREICH ===
echo Du kannst jetzt '2_RECORD.bat' starten.
pause

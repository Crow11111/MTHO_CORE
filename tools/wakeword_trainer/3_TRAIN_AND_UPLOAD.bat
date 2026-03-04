@echo off
echo === ATLAS Wake Word Trainer & Upload ===
echo Startet Training und kopiert Resultat...
echo.

if not exist .venv (
    echo Venv nicht gefunden! Bitte erst '1_SETUP.bat' ausfuehren.
    pause
    exit /b
)

call .venv\Scripts\activate.bat
python scripts/train_model.py
if errorlevel 1 (
    echo Training fehlgeschlagen!
    pause
    exit /b
)

echo.
echo === Kopiervorgang ===
if not exist "models\atlas_custom_verifier.pkl" (
    echo FEHLER: Kein Modell 'atlas_custom_verifier.pkl' gefunden.
    pause
    exit /b
)

REM Ziel-Laufwerk pruefen (Scout Share)
if exist "S:\share\openwakeword\" (
    echo Scout Share gefunden (S:\share\openwakeword).
    copy "models\atlas_custom_verifier.pkl" "S:\share\openwakeword\ATLAS_v1.tflite" /Y
    if errorlevel 1 (
        echo Kopieren fehlgeschlagen! Bitte manuell kopieren.
    ) else (
        echo Kopieren erfolgreich! (Datei als 'ATLAS_v1.tflite' gespeichert)
    )
) else (
    echo WARNUNG: Laufwerk S: nicht gefunden!
    echo Bitte kopiere die Datei manuell:
    echo Quelle: tools\wakeword_trainer\models\atlas_custom_verifier.pkl
    echo Ziel:   /share/openwakeword/ auf dem Home Assistant (als .tflite benennen)
)

echo.
echo WICHTIG: Starte jetzt das Home Assistant 'openWakeWord' Add-on neu!
echo Dann waehle 'ATLAS_v1' in den Einstellungen.
pause

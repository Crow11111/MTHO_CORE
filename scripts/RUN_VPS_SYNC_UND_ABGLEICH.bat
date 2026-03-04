@echo off
chcp 65001 >nul
title VPS: Sync core_directives + Abgleich
set "ROOT=%~dp0.."
cd /d "%ROOT%"

echo.
echo === Voraussetzung: SSH-Tunnel laeuft in einem ANDEREN Fenster ===
echo    Befehl: ssh -L 8000:127.0.0.1:8000 root@187.77.68.250 -N
echo    (Fenster offen lassen.)
echo.
pause

set CHROMA_VPS_HOST=localhost
set CHROMA_VPS_PORT=8000

echo.
echo [1/2] Sync core_directives -> VPS ...
python -m src.scripts.sync_core_directives_to_vps
if errorlevel 1 (
  echo Sync fehlgeschlagen. Ist der Tunnel aktiv?
  pause
  exit /b 1
)

echo.
echo [2/2] Abgleich (VPS core_directives anzeigen) ...
set CHROMA_HOST=localhost
set CHROMA_PORT=8000
python -m src.scripts.check_oc_brain_chroma_abgleich

echo.
echo Fertig. Tunnel-Fenster kann geschlossen werden.
pause

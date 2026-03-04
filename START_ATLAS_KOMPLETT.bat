@echo off
chcp 65001 >nul
title ATLAS Komplett ??? MX-Snapshot + Dienste
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo.
echo === ATLAS Komplett: MX-Snapshot (Sehen) + Backend + Dev-Agent + Voice-Info ===
echo.

REM Port 8555 = camera_snapshot_server (MX/Brio am PC)
netstat -ano 2>nul | findstr /R /C:"LISTENING" /C:"ABH.REN" | findstr ":8555 " >nul
if errorlevel 1 (
  echo [0/4] MX-Snapshot-Server Port 8555... gestartet.
  start "ATLAS MX-Snapshot" cmd /k "python -m src.scripts.camera_snapshot_server"
  timeout /t 2 /nobreak >nul
) else (
  echo [0/4] MX-Snapshot 8555... Port belegt, ueberspringe.
)

call "%ROOT%\START_ATLAS_DIENSTE.bat"




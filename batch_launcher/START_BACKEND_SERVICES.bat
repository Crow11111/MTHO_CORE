@echo off
TITLE MTHO_CORE - BACKEND SERVICES
echo ============================================================
echo MTHO-GENESIS: BACKEND SERVICES (API + WATCHDOG)
echo VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
echo ============================================================

cd /d C:\MTHO_CORE

echo [1/3] Environment Setup (Encoding & Secrets)...
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8

:: Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    pause
    exit
)

echo [2/3] Starte MTHO API Server (Port 8000)...
start "MTHO API" cmd /k "set PYTHONIOENCODING=utf-8 && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload"

echo [3/3] Starte AGOS-0 WATCHDOG (Traum-Injektion & Puls)...
start "MTHO WATCHDOG" cmd /k "set PYTHONIOENCODING=utf-8 && python src/daemons/agos_zero_watchdog.py"

echo [OK] Backend Services gestartet.
echo.
echo Druecke eine Taste zum Beenden dieses Fensters (Dienste laufen weiter).
pause >nul
exit

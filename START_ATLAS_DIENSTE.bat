@echo off
chcp 65001 >nul
title ATLAS Dienste – Starter
set "ROOT=%~dp0"
set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

echo.
echo === ATLAS Dienste starten ===
echo Backend:     http://localhost:8000
echo Dev-Agent:  http://localhost:8501
echo Voice-Info: http://localhost:8502
echo.

REM Prueft, ob auf LocalPort wirklich gelauscht wird (nur LISTENING), nicht irgendeine Verbindung mit dieser Nummer
call :port_listening 8000
if errorlevel 1 (
  echo [1/3] Backend (Port 8000)... gestartet.
  start "ATLAS Backend" cmd /k "cd /d "%ROOT%" && python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
) else (
  echo [1/3] Backend (Port 8000)... Port belegt, ueberspringe.
)

call :port_listening 8501
if errorlevel 1 (
  echo [2/3] Dev-Agent (Port 8501)... gestartet.
  start "ATLAS Dev-Agent" cmd /k "cd /d "%ROOT%" && python -m streamlit run src/ui/dev_agent_console.py --server.port 8501"
) else (
  echo [2/3] Dev-Agent (Port 8501)... Port belegt, ueberspringe.
)

call :port_listening 8502
if errorlevel 1 (
  echo [3/3] Voice-Info (Port 8502)... gestartet.
  start "ATLAS Voice-Info" cmd /k "cd /d "%ROOT%" && python -m streamlit run src/ui/voice_info_console.py --server.port 8502"
) else (
  echo [3/3] Voice-Info (Port 8502)... Port belegt, ueberspringe.
)

echo.
echo Kurz warten, dann Browser oeffnen...
timeout /t 6 /nobreak >nul
start "" "http://localhost:8501"
start "" "http://localhost:8502"

echo.
echo Fertig. Fenster: ATLAS Backend, Dev-Agent, Voice-Info.
echo Zum Beenden: die CMD-Fenster der Dienste schliessen.
echo.
pause
goto :eof

:port_listening
REM Gibt 0 zurueck wenn Port als LISTENING belegt, sonst 1 (Port frei). Verhindert Falschtreffer von netstat/findstr.
netstat -ano 2>nul | findstr "LISTENING" | findstr ":%1 " >nul
if errorlevel 1 exit /b 1
exit /b 0

@echo off
TITLE MTHO_CORE - FRONTEND (STREAMLIT DASHBOARD)
echo ============================================================
echo MTHO-GENESIS: FRONTEND STREAMLIT (Port 8501)
echo ============================================================

cd /d C:\MTHO_CORE

echo [1/1] Starte Streamlit Dashboard...
set PYTHONIOENCODING=utf-8
start "MTHO DASHBOARD" cmd /k "streamlit run src/ui/dashboard.py"

echo [OK] Streamlit wird gestartet...
exit

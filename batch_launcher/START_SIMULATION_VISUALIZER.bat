@echo off
TITLE MTHO_CORE - SIMULATION VISUALIZER (SCHMIEDE)
echo ============================================================
echo MTHO-GENESIS: SIMULATION VISUALIZER (Echtzeit-Schmiede)
echo Zeigt Drehung der Schmiede und Zeitkristall-Status
echo ============================================================

cd /d C:\MTHO_CORE

echo [1/1] Starte Visualizer...
set PYTHONIOENCODING=utf-8
start "MTHO SCHMIEDE VIS" cmd /k "python src/scripts/visualize_reality_check.py --loop"

echo [OK] Visualizer läuft.
exit

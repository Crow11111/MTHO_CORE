# MTHO API Startup Script
# Startet die MTHO API auf Port 8000
# Fuer Task Scheduler oder manuellen Start

$ErrorActionPreference = "Continue"
Set-Location "C:\CORE"

# Aktiviere venv falls vorhanden
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . .venv\Scripts\Activate.ps1
}

# Starte API
Write-Host "[MTHO] Starting API on port 8000..."
python -m src.api.main

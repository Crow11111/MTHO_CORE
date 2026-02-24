# harden_dreadnought.ps1
# ATLAS_CORE: Phase 1 Hardware Hardening Script

Write-Host "=== ATLAS_CORE: Dreadnought Hardening ===" -ForegroundColor Cyan

# 1. Telemetry Level 0 (Windows 11 Enterprise IoT 25H2 Spezifisch)
Write-Host "[*] Deaktiviere Windows Telemetrie (Setze auf Level 0)..."
$telemetryPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection"
if (-not (Test-Path $telemetryPath)) {
    New-Item -Path $telemetryPath -Force | Out-Null
}
Set-ItemProperty -Path $telemetryPath -Name "AllowTelemetry" -Value 0 -Type DWord -Force
Write-Host "[+] Telemetrie erfolgreich auf Level 0 gezwungen." -ForegroundColor Green

# 2. I/O Tuning MaxInstances (Open Thresholds / ChromaDB Latenz Minimierung)
Write-Host "[*] Optimiere I/O MaxInstances auf 20..."
$lanmanPath = "HKLM:\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
if (-not (Test-Path $lanmanPath)) {
    New-Item -Path $lanmanPath -Force | Out-Null
}
Set-ItemProperty -Path $lanmanPath -Name "MaxInstances" -Value 20 -Type DWord -Force
Write-Host "[+] I/O MaxInstances erfolgreich eingestellt." -ForegroundColor Green

Write-Host "=== Hardening abgeschlossen ===" -ForegroundColor Cyan
Write-Host "Hinweis: Diese Anpassungen erfordern eventuell einen Neustart des Systems, um komplett aktiv zu werden." -ForegroundColor Yellow
Write-Host "Druecken Sie eine beliebige Taste, um dieses Fenster zu schliessen..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

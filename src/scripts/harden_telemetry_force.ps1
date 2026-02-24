# harden_telemetry_force.ps1
# Zerstört die verbleibende Windows-Telemetrie und Widgets

Write-Host "=== ATLAS_CORE: Brutal-Hardening (Phase 2) ===" -ForegroundColor Red

# 1. DiagTrack komplett töten
Write-Host "[*] Beende und deaktiviere DiagTrack..."
Stop-Service -Name "DiagTrack" -Force -ErrorAction SilentlyContinue
Set-Service -Name "DiagTrack" -StartupType Disabled -ErrorAction SilentlyContinue

# 2. dmwappushservice deaktivieren
Write-Host "[*] Deaktiviere dmwappushservice..."
Set-Service -Name "dmwappushservice" -StartupType Disabled -ErrorAction SilentlyContinue

# 3. CEIP Scheduled Tasks deaktivieren
Write-Host "[*] Deaktiviere Customer Experience Improvement Program Tasks..."
Disable-ScheduledTask -TaskName "Consolidator" -TaskPath "\Microsoft\Windows\Customer Experience Improvement Program\" -ErrorAction SilentlyContinue
Disable-ScheduledTask -TaskName "UsbCeip" -TaskPath "\Microsoft\Windows\Customer Experience Improvement Program\" -ErrorAction SilentlyContinue

# 4. Compat Appraiser deaktivieren
Write-Host "[*] Deaktiviere Microsoft Compatibility Appraiser..."
Disable-ScheduledTask -TaskName "Microsoft Compatibility Appraiser Exp" -TaskPath "\Microsoft\Windows\Application Experience\" -ErrorAction SilentlyContinue

# 5. Widgets aus Taskleiste entfernen
Write-Host "[*] Entferne Widgets aus der Taskleiste..."
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarDa" -Value 0 -ErrorAction SilentlyContinue

# 6. Widgets per Policy deaktivieren
Write-Host "[*] Deaktiviere News and Interests via Policy..."
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Dsh" -Force -ErrorAction SilentlyContinue | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Dsh" -Name "AllowNewsAndInterests" -Value 0 -ErrorAction SilentlyContinue

Write-Host "[+] Phase 2 Hardening abgeschlossen. Kein automatisches Starten mehr von Spyware-Diensten." -ForegroundColor Green
Write-Host "Tipp: Um die Widgets KOMPLETT vom System zu tilgen, führe dies manuell als Admin aus:" -ForegroundColor Yellow
Write-Host "Get-AppxPackage MicrosoftWindows.Client.WebExperience | Remove-AppxPackage"

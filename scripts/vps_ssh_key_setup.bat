@echo off
title VPS SSH-Key (Hostinger)
set "KEYDIR=%~dp0..\.ssh"
set "KEY=%KEYDIR%\id_ed25519_hostinger"

if not exist "%KEYDIR%" mkdir "%KEYDIR%"

if not exist "%KEY%" (
  echo Erstelle neuen SSH-Key ...
  ssh-keygen -t ed25519 -f "%KEY%" -N "" -q
  echo.
) else (
  echo Key existiert bereits: %KEY%
  echo.
)

echo === Oeffentlichen Schluessel bei Hostinger eintragen (SSH-Schluessel) ===
type "%KEY%.pub"
echo.
echo Kopiere die obige Zeile, dann bei Hostinger: Einstellungen - SSH-Schluessel - + SSH-Schluessel hinzufuegen - einfügen.
pause

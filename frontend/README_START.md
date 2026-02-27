# Dev-Agent starten

## Ein-Klick-Start (empfohlen)

Im **Projekt-Root** (ATLAS_CORE) die Datei **`START_DEV_AGENT.bat`** doppelklicken.

Die Batch-Datei:
- führt **npm install** im Ordner frontend aus (über CMD, nicht PowerShell – umgeht die Ausführungsrichtlinie)
- prüft, ob Port 8000 frei ist; wenn nicht, wird kein zweites Backend gestartet
- startet Backend und Frontend in je einem Fenster
- öffnet nach 10 Sekunden den Browser auf http://localhost:3000

## Falls npm install weiterhin blockiert wird

Wenn du **manuell** im Ordner `frontend` arbeitest und **PowerShell** nutzt, kann `npm install` mit "Ausführung von Skripts deaktiviert" fehlschlagen. Dann:

- **Option A:** `START_DEV_AGENT.bat` einmal ausführen – die Batch läuft in CMD und führt `npm.cmd install` aus.
- **Option B:** In PowerShell einmal erlauben:  
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`  
  Danach z. B. `npm install` im Ordner frontend ausführen.
- **Option C:** In **CMD** (cmd.exe) wechseln: `cd C:\ATLAS_CORE\frontend` und dort `npm install` ausführen.

## Port 8000 bereits belegt

Wenn das Backend-Fenster sofort wieder schließt mit "Port 8000 already in use": Entweder den Starter nur **einmal** ausführen oder den Prozess beenden, der Port 8000 nutzt. Beim nächsten Start prüft die Batch automatisch und startet kein zweites Backend, wenn 8000 belegt ist.

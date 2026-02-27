# Backup-Plan (final) – ATLAS_CORE

**Einziges Backup-Ziel: Hostinger-VPS** (`/var/backups/atlas`). Kein lokales Primärziel, kein S3 – alles geht per Push vom Rechner (Dreadnought) zum VPS.

---

## 1. Ziel

Kritische Projektdaten (Code, Konfiguration, SQLite-DB) täglich automatisiert auf dem Hostinger-VPS sichern. ChromaDB liegt auf dem VPS und wird dort separat gesichert (siehe Abschnitt 5).

## 2. Was wird gesichert?

| Inhalt | Quelle | Anmerkung |
|--------|--------|-----------|
| Anwendungscode | Projekt-Root | Ausschlüsse: `.git`, `__pycache__`, `node_modules`, `*.pyc`, venv, `data/backups`, `logs` |
| Konfiguration | `config/` | Vollständig |
| .env | Projekt-Root | **Nur verschlüsselt** (Fernet); Schlüssel nicht im Backup |
| SQLite-DB | `data/argos_db/*.sqlite` | Vollständig |

ChromaDB-Daten liegen auf dem VPS; Backup der ChromaDB erfolgt auf dem VPS (Cold-Backup, siehe Abschnitt 5).

## 3. Wohin?

- **Ziel:** Hostinger-VPS, Verzeichnis `/var/backups/atlas`
- **Transport:** Push per SSH/SFTP (Paramiko) von Dreadnought aus; der VPS pullt nicht.
- **Berechtigung:** `/var/backups/atlas` wird von `setup_vps_hostinger.py` mit `chmod 700` angelegt (bereits vorhanden).

## 4. Wie wird gesichert? (Automatisierung)

- **Automatisiertes Backup:** Ein Windows Task führt `python src/scripts/daily_backup.py` täglich aus (seit 25.02.2026 aktiv). Das Skript packt den Code (ohne `node_modules`, `.venv` etc.) und lädt ihn per SFTP auf den Hostinger-VPS in `/var/backups/atlas`.
  - Erstellt ein Archiv (tar.gz) aus Code, `config/`, `data/argos_db/`.
  - `.env` wird bei gesetztem `BACKUP_ENCRYPTION_KEY` mit Fernet verschlüsselt und als separate Datei hochgeladen.
  - Upload per SFTP zu `VPS_HOST` mit `VPS_USER` / `VPS_PASSWORD` aus `.env`.
  - **Retention:** Auf dem VPS werden Backups älter als 7 Tage gelöscht (vom Skript per SSH-Befehl ausgeführt).
- **Logging:** `logs/backup.log` (im Projekt); bei Fehlern Eintrag mit Fehlermeldung.
- **Optional:** `HEALTHCHECK_URL` (z. B. healthchecks.io) für erfolgreichen Lauf pingen.

## 5. ChromaDB-Backup (auf dem VPS)

ChromaDB läuft im Container auf dem VPS. Ein Cold-Backup (Container kurz stoppen → Verzeichnis sichern → starten) wird über ein auf dem VPS hinterlegtes Skript und Cron erledigt. Siehe `docs/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md` (Backup-Ziel) und optional `chroma_backup.sh` (Bereitstellung über `setup_vps_hostinger.py`).

## 6. Wann? (Automatisierung)

- **Zeitpunkt:** Täglich, z. B. 04:00 Uhr (Windows: Task Scheduler; Linux: cron).
- **Windows (Task Scheduler):**
  - **Programm:** `C:\ATLAS_CORE\scripts\run_daily_backup.bat`  
  - **Arbeitsverzeichnis:** `C:\ATLAS_CORE`  
  - Oder direkt: Programm `python`, Argument `C:\ATLAS_CORE\src\scripts\daily_backup.py`, Starten in `C:\ATLAS_CORE`.
- **Linux (cron):**  
  `0 4 * * * cd /pfad/zu/ATLAS_CORE && python3 src/scripts/daily_backup.py >> logs/backup.log 2>&1`
- **Windows Task Scheduler (einmalig anlegen):**  
  Als Administrator in cmd/PowerShell:  
  `schtasks /create /tn "ATLAS Daily Backup" /tr "C:\ATLAS_CORE\scripts\run_daily_backup.bat" /sc daily /st 04:00 /ru SYSTEM`  
  (Oder GUI: Aufgabenplanung → Aufgabe erstellen → Trigger täglich 04:00, Aktion: Batch-Datei oder `python …\daily_backup.py`.)

## 7. Aufbewahrung (Retention)

- Die letzten **7** täglichen Backups werden auf dem VPS behalten; ältere werden von `daily_backup.py` beim Upload entfernt.

## 8. Wiederherstellung

- Archiv von `/var/backups/atlas` per SCP/SFTP zurück auf den Rechner, entpacken.
- Falls `.env.enc` gesichert wurde: mit dem gleichen `BACKUP_ENCRYPTION_KEY` entschlüsseln (Fernet).
- **Restore-Test:** Mindestens einmal pro Monat auf Testordner/Staging prüfen.

## 9. Konfiguration (.env)

| Variable | Bedeutung |
|----------|-----------|
| `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` | Bereits vorhanden; werden für Backup-Upload genutzt. |
| `BACKUP_ENCRYPTION_KEY` | Optional. Gültiger Fernet-Key (z. B. aus `Fernet.generate_key().decode()`); wenn gesetzt, wird `.env` verschlüsselt als `.env.enc` ins Archiv aufgenommen. **Empfohlen:** Key in Vaultwarden (Scout) ablegen und bei Bedarf in .env eintragen. |
| `BACKUP_RETENTION_DAYS` | Optional, Standard 7. |
| `HEALTHCHECK_URL` | Optional; URL wird bei Erfolg per GET aufgerufen (z. B. healthchecks.io). |

---

*Konsolidiert aus BACKUP_PLAN.md und Audit-Anmerkungen. Einzige Referenz für Backup-Ziel und -Ablauf.*

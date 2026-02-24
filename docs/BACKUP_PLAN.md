# Täglicher Backup-Plan

## 1. Ziel
Sicherstellung der Datenintegrität und -verfügbarkeit durch automatisierte tägliche Backups aller kritischen Projektdaten.

## 2. Was wird gesichert?
- **Anwendungscode:** Das gesamte Projektverzeichnis (exklusive temporärer Dateien, `node_modules`, `.git`, etc.).
- **Datenbank:** Vollständiger Dump der primären Datenbank (z.B. PostgreSQL, MySQL, SQLite für ATLAS_CORE).
- **Konfigurationsdateien:** `.env`, `config/` Verzeichnis.
- **(Optional) Benutzerdaten/Uploads:** Spezifisches Verzeichnis, falls vorhanden (z.B. `media/`, `uploads/`).

## 3. Wohin wird gesichert?
- **Primär:** Lokaler Backup-Speicher auf dem Server (z.B. `/var/backups/projektname/` bzw. unter Windows ein dediziertes Laufwerk/Ordner).
- **Sekundär:** Externer Cloud-Speicher (z.B. S3-Bucket, Google Cloud Storage) für Offsite-Sicherung.

## 4. Wie wird gesichert? (Automatisierung)
Ein Python-Skript (`scripts/daily_backup.py`) wird erstellt, das folgende Schritte automatisiert:

1. **Datenbank-Dump erstellen** (Beispiel SQLite für ATLAS_CORE):
   - `data/argos_db/`, `*.sqlite` in ein zeitgestempeltes Archiv.

2. **Anwendungscode/Konfiguration archivieren:**
   - Projekt-Root als tar.gz/zip, exkl. `node_modules`, `.git`, `__pycache__`, virtuelle Umgebungen.

3. **Upload zu Cloud-Speicher (optional):** z.B. boto3 für S3.

4. **Retention:** Lokale und Cloud-Backups älter als Aufbewahrungsfrist löschen.

## 5. Wann wird gesichert?
- **Zeitpunkt:** Täglich um 03:00 Uhr UTC (oder Off-Peak-Zeit).
- **Scheduler:** `cron` (Linux) oder Task Scheduler (Windows).

## 6. Aufbewahrungsrichtlinie (Retention)
- Die letzten 7 täglichen Backups werden aufbewahrt.

## 7. Überwachung & Benachrichtigung
- Protokollierung in Log-Datei; bei Fehlern E-Mail oder Slack.

## 8. Wiederherstellungstest
- Mindestens einmal pro Monat vollständiger Wiederherstellungstest auf Staging.

---
*Quelle: Projekt-Plan. Anbindung an ATLAS_CORE siehe docs/DEV_AGENT_UND_SCHNITTSTELLEN.md.*

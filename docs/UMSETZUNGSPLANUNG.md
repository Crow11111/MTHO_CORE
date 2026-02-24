# Umsetzungsplanung ATLAS_CORE

Konkrete Tasks aus Projektplan und Doku. Status: offen / in Arbeit / erledigt.

---

## Task: Tägliches Backup (aus BACKUP_PLAN.md)

**Quelle:** [BACKUP_PLAN.md](BACKUP_PLAN.md)

**Ziel:** Automatisiertes tägliches Backup von Code, Datenbank, Konfig und optional Cloud-Upload.

**Schritte (Umsetzung):**

- [ ] **1** Python-Skript `scripts/daily_backup.py` anlegen:
  - Datenbank: SQLite-Dumps aus `data/argos_db/*.sqlite` in zeitgestempeltes Archiv (z.B. `.tar.gz` / `.zip`).
  - Code + Config: Projekt-Root archivieren, exkl. `node_modules`, `.git`, `__pycache__`, venv.
  - Optional: Upload zu Cloud (z.B. S3 via boto3), wenn Bucket/Keys in `.env`.
  - Retention: Backups älter als 7 Tage löschen (lokal + ggf. Cloud).
  - Logging in Datei (z.B. `logs/backup.log`); bei Fehler optional E-Mail/Slack.
- [ ] **2** Scheduler einrichten:
  - **Windows:** Task Scheduler, täglich z.B. 04:00 Uhr, Aufruf `python C:\ATLAS_CORE\scripts\daily_backup.py`.
  - **Linux:** cron, z.B. `0 4 * * * /usr/bin/python3 /pfad/zu/ATLAS_CORE/scripts/daily_backup.py >> /var/log/atlas_backup.log 2>&1`.
- [ ] **3** Wiederherstellungstest: Einmal pro Monat Restore aus Backup auf Testordner/Staging prüfen.

**Konfiguration (Beispiel .env):**

- `BACKUP_DIR` (lokaler Zielordner)
- Optional: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BACKUP_BUCKET` für Cloud

**Status:** offen

---

*Weitere Tasks werden hier ergänzt. Verweis: DEV_AGENT_UND_SCHNITTSTELLEN.md, BACKUP_PLAN.md.*

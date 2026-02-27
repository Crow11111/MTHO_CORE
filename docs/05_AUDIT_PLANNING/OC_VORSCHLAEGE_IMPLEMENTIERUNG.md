# Vorschläge aus dem OC-Kanal (Implementierungsplan)

Nach Besprechung der offenen Punkte mit OC (über den direkten Kanal) und ggf. Einreichungen aus **rat_submissions/** werden hier **Vorschläge** für Marc zusammengefasst – zur Abstimmung im Rat und zur Übernahme in die Umsetzungsplanung.

---

## Stand

- **Kanal:** ATLAS ↔ OC ist etabliert (ATLAS → OC per Gateway API, OC → ATLAS per rat_submissions).
- **Offene Punkte** wurden an OC übermittelt (siehe oc_diskussion_offene_punkte.md).
- OC kann Vorschläge in workspace/rat_submissions/ ablegen; ATLAS holt sie mit fetch_oc_submissions ab und legt sie unter data/rat_submissions/ ab.

---

## Vorschläge (erste Fassung – aus ATLAS/Agent-Sicht)

Diese Fassung entstand aus der Sicht von ATLAS/Cursor-Agent als **erste Empfehlung**, wie mit den offenen Punkten priorisiert und vorgegangen werden könnte. Sie dient als Diskussionsgrundlage; echte Einreichungen von OC ergänzen oder ersetzen sie nach Abholung aus rat_submissions.

### 1. Sicherheit – Priorität hoch, schrittweise

- **WhatsApp HMAC:** Sobald Webhook-URL und App Secret feststehen, in whatsapp_webhook.py prüfen (HMAC-SHA256). Doku in OFFENE_PUNKTE_AUDIT ergänzen.
- **TLS:** Zuerst Doku klären (wo terminiert TLS: NGROK vs. Reverse-Proxy vs. Let's Encrypt auf VPS). Dann Entscheidung, dann Umsetzung.
- **ChromaDB:** Auf VPS einmalig prüfen; falls -p 8000:8000 dann auf -p 127.0.0.1:8000:8000 umstellen, Zugriff nur per SSH-Tunnel.

### 2. Vaultwarden

- Kurzfristig: BACKUP_ENCRYPTION_KEY manuell in .env (aus Vaultwarden kopiert). Mittelfristig: kleine Anbindung (Skript oder Startup), das bei Bedarf Keys aus Vaultwarden lädt und in Umgebung setzt. Kein Muss für das erste Backup.

### 3. UI / Status-Anzeige

- Ein gemeinsamer Task „Status-Anzeige + Schalter“ (API, Kamera, WhatsApp) in UMSETZUNGSPLANUNG ist sinnvoll. Reihenfolge: zuerst API-Ping und WhatsApp-Kette (HA, rest_command, Webhook), dann Kamera (go2rtc/Snapshot-Status). Frontend: Dev-Agent/Dashboard als Ziel (Streamlit).

### 4. Backup

- Scheduler einmalig einrichten (Windows: Task Scheduler, Linux: cron). Restore-Test als wiederkehrender Termin (z. B. monatlich) in der Doku festhalten.

### 5. OC / getrennte Kanäle

- Getrennte Kanäle als **geplantes Ziel** in der Architektur belassen; Zeitpunkt der Umsetzung von Nutzung und Komplexität abhängig machen. OC-Stammdokumente und Kanal-Doku bereits so formuliert, dass OC keine Steuerbefehle-Chats nutzen soll; konkrete Trennung (z. B. zweite Nummer) wenn der HA-Pfad stabil läuft.

### 6. Optional

- healthchecks.io und ChromaDB Cold-Backup als optionale Tasks; Dev-Agent-Parallel-Skript bei Bedarf (kein Blocker).

---

## Einreichungen von OC

Nach Abholung mit `python -m src.scripts.fetch_oc_submissions` liegen Einreichungen von OC in data/rat_submissions/ (JSON). Sie können hier manuell referenziert oder eingearbeitet werden.

---

Referenz: KANAL_ATLAS_OC.md, UMSETZUNGSPLANUNG.md, OFFENE_PUNKTE_AUDIT.md, oc_diskussion_offene_punkte.md.

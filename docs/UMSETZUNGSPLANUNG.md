# Umsetzungsplanung ATLAS_CORE

Konkrete Tasks aus Projektplan und Doku. Status: offen / in Arbeit / erledigt.

**Hinweis:** Die **offenen Punkte** aus dem Dev-Agent-Audit müssen noch geklärt werden → [OFFENE_PUNKTE_AUDIT.md](OFFENE_PUNKTE_AUDIT.md). Dazu zählen u. a. WhatsApp HMAC, TLS für Webhook, Vaultwarden-Anbindung für Secrets, sowie die unten genannten Tests (MX/Tapo, WhatsApp).

---

## Task: Offene Punkte klären (Priorität)

**Quelle:** [OFFENE_PUNKTE_AUDIT.md](OFFENE_PUNKTE_AUDIT.md)

**Zu klären / zu entscheiden:**

- [ ] **Vaultwarden (Scout):** Nutzung für Secrets (BACKUP_ENCRYPTION_KEY, ggf. API-Keys); Key in Vaultwarden ablegen, bei Bedarf in .env; optional spätere API/CLI-Anbindung.
- [ ] **WhatsApp HMAC:** Meta Signaturprüfung für Webhook; Webhook-URL, App Secret; ggf. Implementierung in whatsapp_webhook.py.
- [ ] **TLS für FastAPI-Webhook:** Wo TLS terminiert (NGROK, Reverse-Proxy, Let's Encrypt); Doku.
- [ ] **ChromaDB auf bestehendem VPS:** Falls noch `-p 8000:8000` → auf `127.0.0.1:8000` umstellen, Zugriff nur per SSH-Tunnel.

**Status:** offen.

---

## Task: Status-Anzeige Kamera & WhatsApp-Webhook (UI/Feedback)

**Ziel:** Nutzer soll sofort sehen, was funktioniert und was nicht – ohne zu raten.

**Kamerastream (MX/Brio, go2rtc, Snapshot-Server):**
- [ ] **Schalter/Button oder Hinweis:** Anzeige, ob der Kamerastream **läuft** oder **nicht läuft** / nicht gestattet / langsam / muss angefordert werden. Optional: Button oder Aktion, um den Stream (oder Snapshot-Server) anzufordern bzw. neu anzustoßen. Wird parallel in AI Studio aufgesetzt; hier im Projekt (z. B. Dashboard/Dev-Agent-Frontend) eine entsprechende Anzeige oder Integration einplanen.

**WhatsApp-Webhook (ATLAS über HA):**
- [ ] **Anzeige Verbindungsstatus:** Welche Teile der Kette sind da, welche fehlen? (z. B. HA erreichbar? rest_command konfiguriert? ATLAS-CORE-API läuft? Webhook-Route erreichbar?) Anzeige, ob etwas **nicht verbunden** ist und ggf. **per Script neu angestoßen** werden muss (z. B. „API starten“, „Snapshot-Server starten“).

**Referenz:** Dashboard/UI siehe [DEV_AGENT_SCHNITTSTELLE_FRONTEND.md](DEV_AGENT_SCHNITTSTELLE_FRONTEND.md); Kamera-Code `go2rtc_client`, `camera_snapshot_server`; WhatsApp `whatsapp_webhook.py`, `ha_client.py`.

**Status:** offen (Anforderung dokumentiert).

---

## Task: Tägliches Backup (Hostinger)

**Quelle:** [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md)

**Ziel:** Automatisiertes tägliches Backup von Code, Datenbank, Konfig zum **Hostinger-VPS** (`/var/backups/atlas`).

**Umsetzung:**

- [x] **1** Skript `src/scripts/daily_backup.py`: Archiv (Code, config/, data/argos_db/), .env nur verschlüsselt (Fernet); Upload per SFTP; Retention 7 Tage auf VPS.
- [ ] **2** Scheduler einrichten (einmalig):
  - **Windows:** Task Scheduler, täglich z.B. 04:00 Uhr, Aufruf `C:\ATLAS_CORE\scripts\run_daily_backup.bat` oder `python C:\ATLAS_CORE\src\scripts\daily_backup.py` mit Arbeitsverzeichnis `C:\ATLAS_CORE`.
  - **Linux:** cron, z.B. `0 4 * * * cd /pfad/zu/ATLAS_CORE && python3 src/scripts/daily_backup.py >> logs/backup.log 2>&1`.
- [ ] **3** Wiederherstellungstest: Einmal pro Monat Restore aus Backup auf Testordner prüfen.

**Konfiguration (.env):** `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` (bereits für VPS-Setup); optional `BACKUP_ENCRYPTION_KEY`, `BACKUP_RETENTION_DAYS`, `HEALTHCHECK_URL`.

**Status:** Skript implementiert; Scheduler manuell einrichten.

---

## Task: WhatsApp – Auslösung, Empfänger, Datum (Implementierung)

**Quelle:** [DEV_AGENT_UND_SCHNITTSTELLEN.md](DEV_AGENT_UND_SCHNITTSTELLEN.md) (Netzarchitektur, Addon gajosu)

**Ziel:** Klarheit: Wo schreibe ich hin, um etwas auszulösen? Wer bekommt die Nachricht genau? Was bekommt der (nur meine Nachrichten, oder alles)?

**Zu klären / umzusetzen:**

- [ ] **1 Wo schreibe ich hin, um ATLAS auszulösen?**  
  Es gibt **keine separate Bot-Nummer**. Das Addon nutzt **deinen** WhatsApp-Account (WhatsApp Web). Du löst aus, indem eine Nachricht **in deinem Account eingeht** – z. B. du schreibst von einem zweiten Gerät an dich selbst, oder ein Kontakt schreibt dir. Die Automation in HA reagiert auf das Event und ruft den Webhook mit dem Payload auf. **Umsetzung:** Doku/Cheat-Sheet für dich: „Nachricht von anderem Gerät an mich selbst“ oder „Kontakt X schreibt mir“ → gleicher Effekt.
- [ ] **2 Wer bekommt die Nachricht genau?**  
  Der **Empfänger** der eingehenden Nachricht (also der Chat, aus dem die Nachricht kam) ist im Payload als `remoteJid` / `sender` (z. B. `491788360264@s.whatsapp.net`). **ATLAS antwortet genau an diesen Absender** über `send_whatsapp(to_number=sender, text=reply)`. Also: Wer dir geschrieben hat, bekommt die Antwort. Wenn du „an dich selbst“ schreibst (anderes Gerät), bekommst du die Antwort in demselben Chat.
- [ ] **3 Was bekommt der Empfänger / was sieht ATLAS?**  
  ATLAS bekommt **alles, was im Event-Payload steht** – das ist die **eine** Nachricht, die gerade eingegangen ist (inkl. Absender, Text, ggf. Audio/Media). Es werden **nicht** dauerhaft alle Chats mitgelesen; nur die Nachricht, die das Event ausgelöst hat. Der Empfänger bekommt **eine Antwort** von ATLAS (Text oder Fehlermeldung), die über HA/Addon an seinen Chat gesendet wird.
- [ ] **4 Optional: WhatsApp-Basis auf Scout**  
  Damit der Kanal auch ohne Dreadnought funktioniert: Basis-Handler (nur Steuerbefehle) auf Scout; rest_command zeigt auf Scout-URL statt Dreadnought. Siehe DEV_AGENT_UND_SCHNITTSTELLEN.md „Latenz & Platzierung“.

**Status:** dokumentiert; Implementierung Basis-Handler auf Scout offen.

---

## Task: MX (Brio) + Tapo – Erkennungstests

**Quelle:** [CAMERA_GO2RTC_WINDOWS.md](CAMERA_GO2RTC_WINDOWS.md), [DEV_AGENT_TESTS_SPEC.md](DEV_AGENT_TESTS_SPEC.md).

**Ziel:** MX (Brio) und Tapo lauffähig testen – Bilder ankommen, Auswertung und Protokoll funktionieren.

**Umsetzung (Dev-Agent-Spec):**
- [x] **Wrapper-Skript:** `src/scripts/run_camera_tests.py` – führt mx_save_images_only, brio_scenario_periodic once, tapo_garden_recognize sequenziell aus.
- [ ] **MX/Brio:** Voraussetzung: go2rtc (localhost:1984, Stream „pc“) **oder** `camera_snapshot_server.py` laufend + `CAMERA_SNAPSHOT_URL`. Dann `python -m src.scripts.run_camera_tests` oder die Einzelskripte.
- [x] **Tapo:** Getestet – `tapo_garden_recognize.py` liefert Frame (RTSP-Fallback) und Erkennung.

**Erfolgskriterien (Spec):** MX mind. 1 .jpg in `data/mx_test/`, Brio mind. 1 Eintrag in `data/brio_scenario/protocol.jsonl`, Tapo mind. 1 .jpg in `data/tapo_garden/`.

**Status:** Tapo grün; MX/Brio abhängig von laufender Bildquelle (go2rtc oder Snapshot-Server).

---

## Task: WhatsApp – Tests von allen Endpunkten

**Quelle:** [dev_agent_whatsapp_context.md](dev_agent_whatsapp_context.md), [DEV_AGENT_TESTS_SPEC.md](DEV_AGENT_TESTS_SPEC.md).

**Ziel:** Konkrete Tests von allen Seiten – ausführbare Prüfungen.

**Umsetzung (Dev-Agent-Spec):**
- [x] **Test-Skript Webhook direkt:** `src/scripts/test_wa_webhook_direct.py` – POST an `/webhook/whatsapp` (simuliert HA). Voraussetzung: ATLAS_CORE API läuft (uvicorn). Aufruf: `python -m src.scripts.test_wa_webhook_direct`.
- [x] **Test-Skript OpenClaw:** `src/scripts/test_wa_openclaw.py` – prüft Gateway-Erreichbarkeit (check_gateway). Aufruf: `python -m src.scripts.test_wa_openclaw`. Getestet: Gateway OK.
- [x] **Von HA aus (E2E):** Skript `src/scripts/run_whatsapp_e2e_ha.py` ruft `rest_command.atlas_whatsapp_webhook` mit addon-ähnlichem Payload auf → gleiche Kette wie echte Nachricht. Voraussetzung: rest_command + Automation in HA (siehe [WHATSAPP_E2E_HA_SETUP.md](WHATSAPP_E2E_HA_SETUP.md)). Manuell: echte Nachricht senden und Antwort im Chat prüfen.

**Status:** Webhook-Direct-, OpenClaw- und E2E-HA-Skript implementiert. OpenClaw vs. HA: [WHATSAPP_OPENCLAW_VS_HA.md](WHATSAPP_OPENCLAW_VS_HA.md).

---

## API-Keys (Hinweis)

API-Keys (Anthropic, Google, etc.) sind **keine Single-Use-Tokens** – sie gelten dauerhaft bis zum Widerruf. Wenn ein Key plötzlich nicht mehr funktioniert: .env prüfen (Variable, keine Anführungszeichen), Console (Limits/Billing), Key nicht widerruft. Siehe [DEV_AGENT_UND_SCHNITTSTELLEN.md](DEV_AGENT_UND_SCHNITTSTELLEN.md) (Abschnitt API-Keys).

---

---

## Task: Parallelisierung (Dev-Agent / APIs)

**Quelle:** [DEV_AGENT_UND_SCHNITTSTELLEN.md](DEV_AGENT_UND_SCHNITTSTELLEN.md), [DEV_AGENT_PARALLEL.md](DEV_AGENT_PARALLEL.md).

**Ziel:** Aufgaben und APIs parallel nutzen (Gemini + Claude, Recherche + Code), um schneller zu antworten.

- [ ] Optional: Skript `src/scripts/dev_agent_parallel.py` – mehrere (instruction, context, model)-Tasks parallel ausführen, Ausgaben in Dateien.
- In .cursorrules und Doku ist hinterlegt: Dev-Agent bei Recherche/Problemen hinzuziehen; Teilaufgaben wo möglich parallel.

**Status:** Doku und Regel aktiv; Skript optional.

---

*Weitere Tasks werden hier ergänzt. Verweis: DEV_AGENT_UND_SCHNITTSTELLEN.md, BACKUP_PLAN_FINAL.md, OFFENE_PUNKTE_AUDIT.md.*

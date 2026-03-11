<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Umsetzungsplanung MTHO_CORE

Konkrete Tasks aus Projektplan und Doku. Status: offen / in Arbeit / erledigt.

**Hinweis:** Die **offenen Punkte** aus dem Dev-Agent-Audit müssen noch geklärt werden → [OFFENE_PUNKTE_AUDIT.md](OFFENE_PUNKTE_AUDIT.md). Dazu zählen u. a. WhatsApp HMAC, TLS für Webhook, Vaultwarden-Anbindung für Secrets, sowie die unten genannten Tests (MX/Tapo, WhatsApp).

---

## Task: OC (OpenClaw) in WhatsApp – getrennte Kanäle & letzte Instanz

**OC = OpenClaw** (Kurzbezeichnung im Projekt).

- [ ] **In Implementierung und Schnittstellen/Architektur aufnehmen:** OC ist im WhatsApp-Kanal aktiv (eigene Session auf dem VPS). Wir werden **später getrennte Kanäle** brauchen: Wenn OC Zugriff auf einen Chat hat, in dem alle verknüpft sind und in dem auch Steuerbefehle ankommen, kann OC damit Dinge außerhalb seiner Umgebung anstoßen, die nicht in seinen Zuständigkeitsbereich gehören.
- [ ] **Jetzt:** Beschränkungen für OC können **bewusst niedriger** sein, um das Gesamtsystem einfacher hochzufahren. **Später:** Diese Lücken wieder schließen (getrennte Kanäle, klare Grenzen).
- [ ] **Generell:** Potenzielle Einfallstore (nicht nur OC, sondern alle Gateways/Messenger-Einstiege) **regelmäßig hinterfragen**; sicherstellen, dass **lokales MTHO** immer die **letzte Entscheidungsgewalt** hat.

**Referenz:** [DEV_AGENT_UND_SCHNITTSTELLEN.md](../02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md) (Netzarchitektur Messenger & OC), [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md).

**Status:** in Planung aufgenommen.

---

## Task: Dev-Agent-Frontend (AI Studio) – Anbindung und Stand

**Ziel:** Chat-UI für den Dev-Agenten (aus AI Studio) an MTHO-CORE-Backend anbinden; ein Klick startet alles.

**Umsetzung (erledigt):**
- [x] Backend: WebSocket `/ws` (chat:send → Dev-Agent → chat:reply), REST `POST /api/services/{name}/restart`, `GET /api/chat/history`. CORS für Frontend-Origin. Siehe [BACKEND_INTEGRATION.md](../../BACKEND_INTEGRATION.md), `src/api/routes/dev_agent_ws.py`.
- [x] Frontend: WebSocket-Client, echte API-Calls statt Mocks; Status „Backend“ (grün/rot) im Header; `VITE_MTHO_API_URL` (Default localhost:8000).
- [x] Starter: `START_DEV_AGENT.bat` – npm install (CMD), Port-Check 8000, startet Backend + Frontend, öffnet Browser.

**Offen / Hinweise:**
- [ ] **Verbindung:** Das Frontend verbindet sich nur, wenn das **Backend läuft**. Wenn „Backend“ rot angezeigt wird: Zuerst Backend starten (oder `START_DEV_AGENT.bat` nutzen, das beides startet). Kein automatischer Neustart bei Verbindungsverlust – Seite neu laden nach Backend-Start.
- [ ] Optional: Retry/Reconnect bei WebSocket-Absturz; Hinweis im UI „Backend starten?“ mit Link zu Doku.

**Referenz:** BACKEND_INTEGRATION.md, frontend/README_START.md.

**Status:** Anbindung umgesetzt; Verbindung abhängig von laufendem Backend.

---

## Task: Stammdokumente und Kanal zu OC – Stand und offene Schritte

**Ziel:** OC hat Kontext (was/warum/wer/wie) und kann mit MTHO/OMEGA_ATTRACTOR Council kommunizieren.

**Aktueller Stand:**

| Was | Wo | OC hat es? |
|-----|-----|------------|
| **Stammdokumente** (Projekt, Marc, Team, OC-Rolle) | Im Repo: `docs/stammdokumente_oc/`. Auf dem VPS: nur nach Ausführung von `deploy_stammdokumente_vps.py`. | **Noch nicht auf dem Server** – Deploy-Skript wurde (nach OMEGA_ATTRACTOR Council-Freigabe) noch nicht ausgeführt. OC kann die Dokumente also nicht im Workspace lesen. |
| **Kanal (Nachricht an OC)** | `send_offene_punkte_to_oc` sendet Kontext + offene Punkte per Gateway-API (`POST /v1/responses`). | **OC hat noch nichts erhalten** – Versand ist bisher an Timeout (oder 405) gescheitert. Gateway muss `/v1/responses` freigeben und ggf. Container neustarten. |

**Was fehlt / nächste Schritte:**

- [ ] **Gateway auf VPS:** In `/var/lib/openclaw/openclaw.json` muss `gateway.http.endpoints.responses.enabled: true` stehen (siehe `setup_vps_hostinger.py`). Danach **OpenClaw-Container neustarten:** `docker restart openclaw-gateway` (per SSH auf dem VPS). Ohne das antwortet das Gateway nicht auf Nachrichten von MTHO (405 oder Timeout).
- [ ] **Nach Neustart:** Erneut `python -m src.scripts.send_offene_punkte_to_oc` ausführen – dann erhält OC Kontext + offene Punkte per Kanal (auch ohne Stammdokumente auf dem Server).
- [ ] **Stammdokumente auf Server (optional, nach OMEGA_ATTRACTOR Council-Freigabe):** `python -m src.scripts.deploy_stammdokumente_vps` – legt die Dokumente unter `/var/lib/openclaw/workspace/stammdokumente/` ab. Danach per WhatsApp OC informieren (Vorlage in [STAMMDOKUMENTE_DEPLOY.md](../04_PROCESSES/STAMMDOKUMENTE_DEPLOY.md)).

**Referenz:** [KANAL_MTHO_OC.md](../02_ARCHITECTURE/KANAL_MTHO_OC.md), [STAMMDOKUMENTE_DEPLOY.md](../04_PROCESSES/STAMMDOKUMENTE_DEPLOY.md), `send_offene_punkte_to_oc.py`, `deploy_stammdokumente_vps.py`.

**Tests / Dev-Agent:** [TEST_SZENARIEN_OC_UND_FRONTEND.md](TEST_SZENARIEN_OC_UND_FRONTEND.md) – Szenarien damit Daten bei OC landen und Frontend ans Backend angebunden ist. Skripte: `test_atlas_oc_channel.py` (--send), `test_frontend_backend.py`, `run_oc_and_frontend_tests.py`. Dev-Agent prüft Kanal-Setup: `python -m src.ai.dev_agent_claude46 "…" docs/dev_agent_oc_kanal_context.md --out=docs/DEV_AGENT_OC_KANAL_CHECKLISTE.md`.

**Status:** Kanal und Stammdokumente vorbereitet; OC hat noch nichts (weder Dateien auf Server noch Nachricht). Neustart Gateway + erneuter Send nötig.

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

**WhatsApp-Webhook (MTHO über HA):**
- [ ] **Anzeige Verbindungsstatus:** Welche Teile der Kette sind da, welche fehlen? (z. B. HA erreichbar? rest_command konfiguriert? MTHO-CORE-API läuft? Webhook-Route erreichbar?) Anzeige, ob etwas **nicht verbunden** ist und ggf. **per Script neu angestoßen** werden muss (z. B. „API starten“, „Snapshot-Server starten“).

**Referenz:** Dashboard/UI siehe [DEV_AGENT_SCHNITTSTELLE_FRONTEND.md](DEV_AGENT_SCHNITTSTELLE_FRONTEND.md); Kamera-Code `go2rtc_client`, `camera_snapshot_server`; WhatsApp `whatsapp_webhook.py`, `ha_client.py`.

**Status:** offen (Anforderung dokumentiert).

---

## Task: Schalter + Anzeige im Frontend (API, Kamera, WhatsApp)

**Ziel:** Im Frontend (Dev-Agent/Dashboard) einen **Schalter** sowie **Anzeige** dafür, dass Dienste laufen bzw. was fehlt – damit du nicht raten musst und ggf. per Klick starten kannst.

- [ ] **MTHO-CORE-API:** Anzeige, ob die API läuft (z. B. Ping `GET /` oder Status-Check); optional Schalter/Button „API starten“ (z. B. startet uvicorn im Hintergrund oder öffnet Hinweis zum manuellen Start).
- [ ] **Kamerastream (MX/go2rtc/Snapshot-Server):** Anzeige, ob der Stream/Snapshot erreichbar ist; optional Schalter „Snapshot-Server starten“ oder Hinweis „go2rtc starten“.
- [ ] **WhatsApp-Webhook-Kette:** Anzeige, welche Teile der Verbindung stehen (HA erreichbar? MTHO-Webhook erreichbar? rest_command konfiguriert?) und ob etwas neu angestoßen werden muss.

**Referenz:** [DEV_AGENT_SCHNITTSTELLE_FRONTEND.md](DEV_AGENT_SCHNITTSTELLE_FRONTEND.md), Task „Status-Anzeige Kamera & WhatsApp-Webhook“ oben.

**Status:** offen.

---

## Task: Tägliches Backup (Hostinger)

**Quelle:** [BACKUP_PLAN_FINAL.md](../03_INFRASTRUCTURE/BACKUP_PLAN_FINAL.md)

**Ziel:** Automatisiertes tägliches Backup von Code, Datenbank, Konfig zum **Hostinger-VPS** (`/var/backups/atlas`).

**Umsetzung:**

- [x] **1** Skript `src/scripts/daily_backup.py`: Archiv (Code, config/, data/argos_db/), .env nur verschlüsselt (Fernet); Upload per SFTP; Retention 7 Tage auf VPS.
- [ ] **2** Scheduler einrichten (einmalig):
  - **Windows:** Task Scheduler, täglich z.B. 04:00 Uhr, Aufruf `C:\MTHO_CORE\scripts\run_daily_backup.bat` oder `python C:\MTHO_CORE\src\scripts\daily_backup.py` mit Arbeitsverzeichnis `C:\MTHO_CORE`.
  - **Linux:** cron, z.B. `0 4 * * * cd /pfad/zu/MTHO_CORE && python3 src/scripts/daily_backup.py >> logs/backup.log 2>&1`.
- [ ] **3** Wiederherstellungstest: Einmal pro Monat Restore aus Backup auf Testordner prüfen.

**Konfiguration (.env):** `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` (bereits für VPS-Setup); optional `BACKUP_ENCRYPTION_KEY`, `BACKUP_RETENTION_DAYS`, `HEALTHCHECK_URL`.

**Status:** Skript implementiert; Scheduler manuell einrichten.

---

## Task: WhatsApp – Auslösung, Empfänger, Datum (Implementierung)

**Quelle:** [DEV_AGENT_UND_SCHNITTSTELLEN.md](../02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md) (Netzarchitektur, Addon gajosu)

**Ziel:** Klarheit: Wo schreibe ich hin, um etwas auszulösen? Wer bekommt die Nachricht genau? Was bekommt der (nur meine Nachrichten, oder alles)?

**Zu klären / umzusetzen:**

- [ ] **1 Wo schreibe ich hin, um MTHO auszulösen?**  
  Es gibt **keine separate Bot-Nummer**. Das Addon nutzt **deinen** WhatsApp-Account (WhatsApp Web). Du löst aus, indem eine Nachricht **in deinem Account eingeht** – z. B. du schreibst von einem zweiten Gerät an dich selbst, oder ein Kontakt schreibt dir. Die Automation in HA reagiert auf das Event und ruft den Webhook mit dem Payload auf. **Umsetzung:** Doku/Cheat-Sheet für dich: „Nachricht von anderem Gerät an mich selbst“ oder „Kontakt X schreibt mir“ → gleicher Effekt.
- [ ] **2 Wer bekommt die Nachricht genau?**  
  Der **Empfänger** der eingehenden Nachricht (also der Chat, aus dem die Nachricht kam) ist im Payload als `remoteJid` / `sender` (z. B. `491788360264@s.whatsapp.net`). **MTHO antwortet genau an diesen Absender** über `send_whatsapp(to_number=sender, text=reply)`. Also: Wer dir geschrieben hat, bekommt die Antwort. Wenn du „an dich selbst“ schreibst (anderes Gerät), bekommst du die Antwort in demselben Chat.
- [ ] **3 Was bekommt der Empfänger / was sieht MTHO?**  
  MTHO bekommt **alles, was im Event-Payload steht** – das ist die **eine** Nachricht, die gerade eingegangen ist (inkl. Absender, Text, ggf. Audio/Media). Es werden **nicht** dauerhaft alle Chats mitgelesen; nur die Nachricht, die das Event ausgelöst hat. Der Empfänger bekommt **eine Antwort** von MTHO (Text oder Fehlermeldung), die über HA/Addon an seinen Chat gesendet wird.
- [ ] **4 Optional: WhatsApp-Basis auf Scout**  
  Damit der Kanal auch ohne 4D_RESONATOR (MTHO_CORE) funktioniert: Basis-Handler (nur Steuerbefehle) auf Scout; rest_command zeigt auf Scout-URL statt 4D_RESONATOR (MTHO_CORE). Siehe DEV_AGENT_UND_SCHNITTSTELLEN.md „Latenz & Platzierung“.

**Status:** dokumentiert; Implementierung Basis-Handler auf Scout offen.

---

## Task: MX (Brio) + Tapo – Erkennungstests

**Quelle:** [CAMERA_GO2RTC_WINDOWS.md](../03_INFRASTRUCTURE/CAMERA_GO2RTC_WINDOWS.md), [DEV_AGENT_TESTS_SPEC.md](../04_PROCESSES/DEV_AGENT_TESTS_SPEC.md).

**Ziel:** MX (Brio) und Tapo lauffähig testen – Bilder ankommen, Auswertung und Protokoll funktionieren.

**Umsetzung (Dev-Agent-Spec):**
- [x] **Wrapper-Skript:** `src/scripts/run_camera_tests.py` – führt mx_save_images_only, brio_scenario_periodic once, tapo_garden_recognize sequenziell aus.
- [ ] **MX/Brio:** Voraussetzung: go2rtc (localhost:1984, Stream „pc“) **oder** `camera_snapshot_server.py` laufend + `CAMERA_SNAPSHOT_URL`. Dann `python -m src.scripts.run_camera_tests` oder die Einzelskripte.
- [x] **Tapo:** Getestet – `tapo_garden_recognize.py` liefert Frame (RTSP-Fallback) und Erkennung.

**Erfolgskriterien (Spec):** MX mind. 1 .jpg in `data/mx_test/`, Brio mind. 1 Eintrag in `data/brio_scenario/protocol.jsonl`, Tapo mind. 1 .jpg in `data/tapo_garden/`.

**Status:** Tapo grün; MX/Brio abhängig von laufender Bildquelle (go2rtc oder Snapshot-Server).

---

## Task: WhatsApp – Tests von allen Endpunkten

**Quelle:** [dev_agent_whatsapp_context.md](dev_agent_whatsapp_context.md), [DEV_AGENT_TESTS_SPEC.md](../04_PROCESSES/DEV_AGENT_TESTS_SPEC.md).

**Ziel:** Konkrete Tests von allen Seiten – ausführbare Prüfungen.

**Umsetzung (Dev-Agent-Spec):**
- [x] **Test-Skript Webhook direkt:** `src/scripts/test_wa_webhook_direct.py` – POST an `/webhook/whatsapp` (simuliert HA). Voraussetzung: MTHO_CORE API läuft (uvicorn). Aufruf: `python -m src.scripts.test_wa_webhook_direct`.
- [x] **Test-Skript OpenClaw:** `src/scripts/test_wa_openclaw.py` – prüft Gateway-Erreichbarkeit (check_gateway). Aufruf: `python -m src.scripts.test_wa_openclaw`. Getestet: Gateway OK.
- [x] **Von HA aus (E2E):** Skript `src/scripts/run_whatsapp_e2e_ha.py` ruft `rest_command.atlas_whatsapp_webhook` mit addon-ähnlichem Payload auf → gleiche Kette wie echte Nachricht. Voraussetzung: rest_command + Automation in HA (siehe [WHATSAPP_E2E_HA_SETUP.md](../03_INFRASTRUCTURE/WHATSAPP_E2E_HA_SETUP.md)). Manuell: echte Nachricht senden und Antwort im Chat prüfen.

**Status:** Webhook-Direct-, OpenClaw- und E2E-HA-Skript implementiert. OpenClaw vs. HA: [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md).

---

## API-Keys (Hinweis)

API-Keys (Anthropic, Google, etc.) sind **keine Single-Use-Tokens** – sie gelten dauerhaft bis zum Widerruf. Wenn ein Key plötzlich nicht mehr funktioniert: .env prüfen (Variable, keine Anführungszeichen), Console (Limits/Billing), Key nicht widerruft. Siehe [DEV_AGENT_UND_SCHNITTSTELLEN.md](../02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md) (Abschnitt API-Keys).

---

---

## Task: Parallelisierung (Dev-Agent / APIs)

**Quelle:** [DEV_AGENT_UND_SCHNITTSTELLEN.md](../02_ARCHITECTURE/DEV_AGENT_UND_SCHNITTSTELLEN.md), [DEV_AGENT_PARALLEL.md](../04_PROCESSES/DEV_AGENT_PARALLEL.md).

**Ziel:** Aufgaben und APIs parallel nutzen (Gemini + Claude, Recherche + Code), um schneller zu antworten.

- [ ] Optional: Skript `src/scripts/dev_agent_parallel.py` – mehrere (instruction, context, model)-Tasks parallel ausführen, Ausgaben in Dateien.
- In .cursorrules und Doku ist hinterlegt: Dev-Agent bei Recherche/Problemen hinzuziehen; Teilaufgaben wo möglich parallel.

**Status:** Doku und Regel aktiv; Skript optional.

---

*Weitere Tasks werden hier ergänzt. Verweis: DEV_AGENT_UND_SCHNITTSTELLEN.md, BACKUP_PLAN_FINAL.md, OFFENE_PUNKTE_AUDIT.md.*

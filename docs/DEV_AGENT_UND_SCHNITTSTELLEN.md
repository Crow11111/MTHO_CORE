# Dev-Agent & Schnittstellenbeschreibung

## Dev-Agent (ATLAS_DEV_AGENT)

### Modell
- **ATLAS-Ausgabe erfolgt ausschließlich über Pro-Tier-Modelle.** Flash/Leichtgewichte sind für produktive ATLAS-Antworten nicht vorgesehen.
- **Standard:** Gemini 3.1 Pro (`gemini-3.1-pro-preview`) über `GEMINI_API_KEY` aus `.env`.
- **Wahl per .env:** `GEMINI_DEV_AGENT_MODEL` (z.B. `gemini-3.1-pro-preview`, `gemini-3-pro-preview`, `gemini-2.5-pro`).
- **Später (optional):** Claude 4.6 / 3.5, sobald der Anthropic-Account die Modelle freischaltet.

### Abbrechen / Timeout
- **Streamlit blockiert** während des LLM-Aufrufs; es gibt derzeit **keinen Abbrechen-Button** in der UI.
- **Abbrechen:** Browser-Tab schließen oder im Terminal, in dem Streamlit läuft, **Strg+C** drücken (ggf. mehrfach). Prozess kill beendet den Request.
- Ein technisches Request-Timeout (z.B. 120 s) kann ergänzt werden; echter „Abbrechen“-Button erfordert asynchrone Ausführung (geplante Erweiterung).

### Vernetzung mit dem Rest des Projekts
- Der Dev-Agent liefert **Text (und optional Sprache über ElevenLabs)**. Code-Vorschläge, Refactor-Pläne oder Konfigurationssnippets müssen **manuell** in die entsprechenden Dateien/Strukturen übernommen werden, bis eine spätere Integration (z.B. Patch-Anwendung, Datei-Schreibfunktion) gebaut wird.
- **Rollen & STATE** kommen aus `src/config/voice_config.py` (Osmium Circle); Schnittstelle für TTS: `src/voice/elevenlabs_tts.py`.

### Dev-Agent Console (Streamlit) – Start & Oberfläche

Kleines Tool zur Bedienung des Dev-Agenten über eine lokale Web-UI (ohne Cursor-Chat/Consumer-Quota).

**Starten:**

```bash
cd C:\ATLAS_CORE
streamlit run src/ui/dev_agent_console.py
```

Alternativ mit explizitem Python: `python -m streamlit run src/ui/dev_agent_console.py`. Der Browser öffnet sich automatisch (Standard: http://localhost:8501).

**Im Browser:**

- **Titel:** „ATLAS_DEV_AGENT // CLAUDE 4.6“ (Backend ist aktuell Gemini; Titel aus historischen Gründen).
- **Checkbox:** „Sprache (ElevenLabs) aktiv“ – an/aus für TTS-Ausgabe der Antwort.
- **Dropdown „Rolle“:** Auswahl aus `OSMIUM_VOICE_CONFIG` (z.B. atlas_dialog, therapeut, analyst). Gilt für die ElevenLabs-Stimme, wenn Sprache aktiv ist.
- **Dropdown „STATE“:** Optionaler emotionaler Zustand (z.B. „— none —“, „[STATE: Internal-Crisis]“). Wird bei TTS als Präfix genutzt.
- **Textfeld:** „Aufgabe / Prompt an Claude 4.6“ – hier die Anfrage an den Dev-Agenten eingeben.
- **Button „▶ AUSFÜHREN“:** Sendet den Prompt an das konfigurierte LLM-Backend (Gemini); Antwort erscheint unter „Antwort (Text)“; bei aktivierter Sprache wird zusätzlich ElevenLabs aufgerufen (Rolle + STATE).

**Code:** `src/ui/dev_agent_console.py` (Streamlit), Backend: `src/ai/dev_agent_claude46.py` (`call_dev_agent`), TTS: `src/voice/elevenlabs_tts.py`.

**Modell-Auswahl:** In der UI wählbar (Dropdown); Backend unterstützt `call_dev_agent(..., model="gemini-3.1-pro-preview"` bzw. `claude-sonnet-4-5` etc.). Liste der zulässigen Modelle: `DEV_AGENT_MODELS` in `dev_agent_claude46.py`. Mini-Schnittstellenbeschreibung für den Bau eines eigenen Frontends: [DEV_AGENT_SCHNITTSTELLE_FRONTEND.md](DEV_AGENT_SCHNITTSTELLE_FRONTEND.md).

### Dev-Agent in der Coding-Prozedur
- **Einzelne Tasks an den Dev-Agent übergeben:** Bei Coding- und Refactoring-Aufgaben im Projekt sollen konkrete Teilaufgaben (z.B. „Implementiere Funktion X in Modul Y“, „Schreibe Tests für …“, „Dokumentiere Schnittstelle Z“) an den **Dev-Agent** (Streamlit + Gemini/Claude) übergeben werden, statt alles nur im Cursor-Chat zu erledigen. Der Dev-Agent arbeitet mit dem gleichen Codebase-Kontext und liefert umsetzbare Vorschläge; Übernahme in die Dateien erfolgt manuell oder per Copy-Paste.
- **Sinnvoll bei:** Implementierungsdetails, Modul-API-Design, Testfälle, Doku-Formulierungen, mehrstufige Refactor-Schritte. Cursor/Agent bleibt für schnelle Edits, Grep, Struktur; der Dev-Agent für durchdachte, atomisierte Tasks.
- **Automatisch:** Der Cursor-Agent nutzt den Dev-Agent von sich aus, wenn es passt – keine dezidierte Anweisung nötig.

### Dev-Agent bei Recherche und Problemen (Standard)
- **Recherche oder etwas klappt nicht:** Wenn etwas zu recherchieren ist oder ein Problem vorliegt (z.B. Fehler, unklare API, „warum funktioniert X nicht?“), soll der **Dev-Agent standardmäßig hinzugezogen** werden: Kontext (Fehlermeldung, relevante Doku, Codeausschnitt) als Kontextdatei oder im Prompt übergeben, Dev-Agent liefert Analyse und mögliche Ursachen. Das kann schneller sein, als alles nacheinander allein im Cursor-Agent zu klären – der Dev-Agent kann parallel „nachdenken“ (Aufruf ausführen), während der Agent andere Schritte vorbereitet.
- **Vorgehen:** Aufgabe formulieren („Recherchiere …“, „Woran könnte es liegen, dass …“) + Kontext (Datei/Pfad oder Text) → `python -m src.ai.dev_agent_claude46 "…" [kontext.md] --out=docs/…`; Ergebnis lesen und in die nächste Aktion einfließen lassen.

### Parallelisierung (APIs / Tasks)
- **Logik:** Aufgaben und Anfragen sollen wo möglich **parallel** genutzt werden, um die verschiedenen APIs (Gemini, Claude, ggf. andere) zu entlasten und schneller zu antworten. Konkret: (1) **Sub-Tasks aufteilen** – z.B. Teil A an Dev-Agent (Gemini), Teil B an Dev-Agent (Claude), oder Recherche an Dev-Agent während der Cursor-Agent Code prüft. (2) **Technisch:** Ein Skript oder eine kleine Bibliothek, die mehrere `call_dev_agent`-Aufrufe (oder HTTP-Calls an verschiedene Backends) in **concurrent.futures** oder **asyncio** parallel startet und Ergebnisse sammelt, kann gebaut werden (siehe `docs/DEV_AGENT_PARALLEL.md` oder Umsetzungsplanung). (3) **Heuristik:** Wenn eine Anfrage in 2–3 unabhängige Teilfragen zerlegbar ist, diese parallel an Dev-Agent/APIs schicken und Antworten zusammenführen.

---

## Backup

- **Plan (final):** [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md) – **einziges Backup-Ziel: Hostinger-VPS** (`/var/backups/atlas`). Kein S3, kein lokales Primärziel.
- **Umsetzung:** Skript `src/scripts/daily_backup.py` – archiviert Code, `config/`, `data/argos_db/`; `.env` nur verschlüsselt (Fernet), wenn `BACKUP_ENCRYPTION_KEY` gesetzt; Push per SFTP zum VPS; Retention 7 Tage (lokal auf VPS gelöscht). Automatisierung: Windows Task Scheduler oder cron (siehe BACKUP_PLAN_FINAL.md).
- **Relevante Pfade:** Projekt-Root, `data/argos_db/`, `config/`, `.env` (nur verschlüsselt).

### Dev-Agent-Review (Schnittstellen / Architektur / Sicherheit / Backup)

- **Kontextdatei:** [docs/dev_agent_review_context.md](dev_agent_review_context.md) – Zusammenfassung der zentralen Doku für einen Review durch den Dev-Agent.
- **Aufruf:** `python -m src.ai.dev_agent_claude46 "Prüfe die Dokumente …" docs/dev_agent_review_context.md` (vollständige Anweisung und Ausgabe in Datei siehe am Ende von `dev_agent_review_context.md`).

---

## Netzarchitektur: Messenger & OpenClaw

### Aktuell: ATLAS-Core-WhatsApp (Home Assistant)

- **Pfad:** WhatsApp → Home Assistant (WhatsApp-Addon) → `rest_command.atlas_whatsapp_webhook` → ATLAS_CORE FastAPI (`/webhook/whatsapp`) → LLM/TTS/HA-Services. **E2E-Setup und Test:** [WHATSAPP_E2E_HA_SETUP.md](WHATSAPP_E2E_HA_SETUP.md); Skript `run_whatsapp_e2e_ha.py` löst die Kette über den HA-Service aus. **OpenClaw vs. HA:** [WHATSAPP_OPENCLAW_VS_HA.md](WHATSAPP_OPENCLAW_VS_HA.md).
- **Code:** `src/api/routes/whatsapp_webhook.py`, `src/network/ha_client.py` (HASS_URL, HASS_TOKEN).

**Addon (gajosu/whatsapp-ha-addon):** Das Addon verbindet sich per **WhatsApp Web** mit **deinem eigenen** WhatsApp-Account. Es gibt **keine separate „Bot-Nummer“** – der Empfang läuft über deinen Account; alle eingehenden Nachrichten (in deine Chats) können als Event an HA gemeldet werden. Der Event-Payload enthält z.B. `key.remoteJid` (Chat-ID, Format z.B. `491788360264@s.whatsapp.net`) und die Nachricht. ATLAS antwortet mit `send_whatsapp(to_number=sender)` – also an genau diesen `remoteJid` (den Absender der eingehenden Nachricht). Beim **Versand** im Addon kannst du Sender/Empfänger manuell anpassen (Nummer im Format `…@s.whatsapp.net`). **Wo du „die Nummer“ herkriegst:** Du holst keine extra Nummer – dein Account ist der Addon-Account. Die „Nummer“, an die ATLAS zurückschreibt, ist der **Absender** aus dem Event (`remoteJid`/`sender`), also der Chat, aus dem die Nachricht kam. Um ATLAS zu nutzen: Eine Nachricht muss in deinem Account **eingehen** (z.B. von einem Kontakt oder von dir aus einem anderen Gerät); die Automation leitet sie an ATLAS weiter, die Antwort kommt in denselben Chat.

### OpenClaw (Hostinger)

- **Rolle:** Selbst gehostetes **Gateway** zwischen Messenger (WhatsApp, Telegram, Discord, iMessage) und AI-Agents. Läuft auf Hostinger; Referenz: [OpenClaw Docs](https://docs.openclaw.ai/).
- **Konfiguration:** z.B. `~/.openclaw/openclaw.json`; `channels.whatsapp.allowFrom` mit erlaubten Nummern (z.B. `["+491788360264"]`).
- **Bezug zu ATLAS_CORE:** OpenClaw ist ein **zweiter, optionaler Einstieg** für Chat-to-Agent (z.B. mit Anthropic). Kein Ersatz für den ATLAS-Webhook; entweder zwei getrennte Wege (zwei Nummern/Instanzen) oder spätere Brücke (OpenClaw-API ↔ ATLAS).
- **In .env:** `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD`, **`OPENCLAW_GATEWAY_TOKEN`** (Gateway-Token von Hostinger). ATLAS_CORE liest den Token in `src/network/openclaw_client.py`; konkrete API-Anbindung (z.B. Nachrichten an Gateway senden/empfangen) nutzt diesen Token bei Bedarf.
- **Sandbox-Pflicht:** OpenClaw muss auf dem VPS **isoliert** laufen (z. B. eigener Docker-Container), sodass er **keinen Zugriff** auf andere Dienste auf demselben Server hat (kein ChromaDB, kein Ollama, keine .env/Keys). Details: [VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md](VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md).

### Übersicht

| Einstieg            | Ziel                         | Konfiguration / Code                    |
|---------------------|------------------------------|-----------------------------------------|
| HA WhatsApp-Webhook | ATLAS (Lights, TTS, LLM)     | `whatsapp_webhook.py`, HA rest_command  |
| OpenClaw (Hostinger)| Claw-Bot / Agent (z.B. Pi)   | OpenClaw Gateway, allowFrom, Docs       |

### Wie sende ich Anfragen und bekomme Antwort? (WhatsApp)

- **ATLAS (über Home Assistant):**  
  Das Addon nutzt **deinen** WhatsApp-Account (WhatsApp Web). Jede **eingehende** Nachricht in deinem Account kann (per Automation) an ATLAS weitergeleitet werden. Du schickst also z.B. von deinem Handy eine Nachricht **an einen Chat, der auf deinem Account ankommt** (z.B. von einem zweiten Gerät an dich selbst, oder ein Kontakt schreibt dir). HA feuert das Event, ruft `rest_command.atlas_whatsapp_webhook` mit dem Payload (inkl. `remoteJid` = Absender) auf, ATLAS antwortet mit **`send_whatsapp(to_number=sender, text=reply)`** – die Antwort erscheint **im selben Chat** beim Absender. Es gibt keine extra „HA-WhatsApp-Nummer“ zum Anschreiben; die „Nummer“ für die Antwort ist immer der **Absender** aus dem Event.
- **OpenClaw (Hostinger):**  
  OpenClaw hat eine **eigene** WhatsApp-Verbindung (andere Instanz). Du schickst an die **mit OpenClaw verknüpfte Nummer**; der Agent antwortet im gleichen Chat. `allowFrom` (WHATSAPP_TARGET_ID) in ATLAS legt fest, von welcher Nummer Nachrichten erlaubt sind.

**Kurz:** ATLAS antwortet in den Chat, aus dem die Nachricht kam (Absender = `remoteJid`). OpenClaw = eigener Kanal mit eigener Nummer.

### Latenz & Platzierung: WhatsApp-Basis auf Scout vs. Hostinger

- **Latenz und Performance** sind entscheidend: Steuerbefehle („Licht Bad aus“) sollen schnell ausgeführt werden; die Antwort soll aus demselben Kontext kommen wie die lokale HA (Lichter, Sensoren).
- **Empfehlung:** Der **WhatsApp-Basis-Handler** (nur klare Steuerkommandos, ohne Dreadnought) läuft auf dem **Scout (Pi)** – dort läuft HA ohnehin, der Handler ruft HA lokal auf (geringe Latenz), und der Kanal funktioniert auch, wenn der Dreadnought aus ist.
- **Hostinger** eignet sich für: OpenClaw, ChromaDB, Backup; optional eine **zweite HA-Instanz**, die mit der lokalen HA verknüpft ist (mehrere Home-Assistant-Instanzen können gemeinsam ein Zuhause steuern und voneinander wissen). Dann könnte z.B. von unterwegs über Hostinger-HA auf die lokale HA zugegriffen werden – Aufteilung nach Latenz und Verfügbarkeit.
- **Zusammenfassung:** Basis-WhatsApp und erste Reaktion = Scout (niedrige Latenz, unabhängig vom PC). Schwere LLM-Aufgaben und zweite HA = optional Hostinger.

### VPS-Setup (automatisiert)

- **Skript:** `src/scripts/setup_vps_hostinger.py` – richtet per SSH auf dem Hostinger-VPS ein: Docker, Firewall (22, 18789, 8000, 80/443), Netzwerk `openclaw_net`, ChromaDB-Container (`chroma-atlas`, Port 8000), Backup-Verzeichnis `/var/backups/atlas`, OpenClaw-Gateway in Sandbox (Config + SOUL.md + Channels).
- **OpenClaw-Config:** Token aus `OPENCLAW_GATEWAY_TOKEN`; Channels aus .env: WhatsApp `allowFrom` aus `WHATSAPP_TARGET_ID`, optional `TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`. ATLAS/ARGOS-System-Prompt-Framing wird als `SOUL.md` ins Workspace geschrieben.
- **Hilfsskripte:** `src/scripts/check_openclaw_vps.py` (Status/Logs OpenClaw), `src/scripts/find_soul_on_vps.py` (Suche SOUL.md auf VPS), `src/scripts/test_vps_ssh.py` (SSH-Test).
- **Ausführung:** `python src/scripts/setup_vps_hostinger.py` (idempotent; .env: VPS_HOST, VPS_USER, VPS_PASSWORD, OPENCLAW_GATEWAY_TOKEN).

---

## Go2RTC / Kamera (PC oder Scout)

- **Rolle:** Kamerastream für ATLAS (Snapshots, ggf. Stream-URLs für HA). go2rtc kann **auf dem PC** (Windows, Brio) oder **auf dem Scout (Pi)** laufen – ATLAS spricht immer dieselbe API an.
- **Empfohlene Alternative:** **go2rtc auf dem Scout** läuft stabil; wenn die Brio am PC Probleme macht (Stream bricht ab), einfach auf den Scout umstellen: In .env `GO2RTC_BASE_URL` auf die Scout-Adresse setzen (z.B. `http://192.168.x.x:1984` oder `http://scout.local:1984`), `GO2RTC_STREAM_NAME` auf den auf dem Scout konfigurierten Stream-Namen (z.B. `pc` oder wie dort angelegt). Kein Code-Umbau nötig – nur Konfiguration.
- **PC (Brio):** go2rtc aus `driver/go2rtc_win64/`; Standard-API localhost:1984. Doku/Troubleshooting: [CAMERA_GO2RTC_WINDOWS.md](CAMERA_GO2RTC_WINDOWS.md).
- **FFmpeg:** Skripte (Tapo RTSP, Brio Snapshot-Server, MP4→JPEG) nutzen **zuerst** `driver/go2rtc_win64/ffmpeg.exe` mit Arbeitsverzeichnis = dieser Ordner (damit DLLs gefunden werden). Sonst PATH oder .env `FFMPEG_PATH`. So bleiben stabile Streams/Abfragen ohne System-FFmpeg-Konflikte.
- **In .env:** `GO2RTC_BASE_URL` (PC/Scout), `GO2RTC_STREAM_NAME`. Optional für **On-Demand-Webcam** (Brio nur bei Abruf): `CAMERA_SNAPSHOT_URL=http://localhost:8555/snapshot.jpg` – dann liefert `get_snapshot()` das Bild vom Snapshot-Server (Kamera-LED nur bei Abruf an).
- **Code:** `src/network/go2rtc_client.py` – `snapshot_url()`, `get_snapshot()`, `is_configured()`. Test: `python src/scripts/test_go2rtc_snapshot.py`. On-Demand-Server: `python src/scripts/camera_snapshot_server.py`. Tapo (Balkon/Garten): `python src/scripts/tapo_garden_recognize.py`.
- **Dokumentation:** [CAMERA_GO2RTC_WINDOWS.md](CAMERA_GO2RTC_WINDOWS.md) (Brio/Windows + **Alternative Scout**).

---

## ChromaDB (Vektor-DB / RAG)

- **Rolle:** Vektor-Datenbank für RAG (u. a. ND-Insights, argos_knowledge_graph). Laut [03_DATENBANK_VECTOR_STORE_OSMIUM.md](../data/antigravity_docs_osmium/03_DATENBANK_VECTOR_STORE_OSMIUM.md) Collections: `argos_knowledge_graph`, `core_brain_registr`, `krypto_scan_buffer`.
- **Lokal (Standard):** `PersistentClient` mit `CHROMA_LOCAL_PATH` (z. B. `c:\ATLAS_CORE\data\chroma_db`).
- **Remote (VPS):** Wenn `CHROMA_HOST` in `.env` gesetzt ist, nutzt ATLAS_CORE `HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)` – typisch Port 8000. Chroma-Server auf dem VPS muss laufen (`chroma run --path /pfad` o. ä.).
- **Code:** `src/network/chroma_client.py` – `get_chroma_client()`, `get_collection(name)`. Ingest: `src/scripts/ingest_nd_insights_to_chroma.py`.

---

## Externe Dienste (Consumer / Developer / Business)

- **Klarstellung:** ATLAS_CORE nutzt durchgängig **eigene API-Keys** (`.env`). Abrechnung erfolgt direkt beim Anbieter (Google, Anthropic, ElevenLabs); es gibt keine versteckte „Consumer-Quota“ im Projektcode.
- **API-Keys sind keine Single-Use-Tokens:** Keys von Anthropic, Google usw. gelten **dauerhaft**, bis du sie in der Console widerrufst. Wenn ein Key plötzlich 401/ungültig meldet: (1) In .env prüfen, ob die Variable exakt stimmt (z. B. `ANTHROPIC_API_KEY`) und der Wert ohne Anführungszeichen/Zeilenumbruch steht. (2) In der Anbieter-Console: Limits/Billing prüfen (Rate-Limit, Guthaben). (3) Key nicht versehentlich widerrufen oder durch einen anderen ersetzt haben. Ein neuer Key ist nur nötig, wenn der alte widerrufen wurde oder ungültig ist – nicht nach jeder Anfrage.
- **Vaultwarden (Scout):** Auf dem Scout läuft Vaultwarden; sinnvoll für zentrale Ablage von Secrets (z. B. BACKUP_ENCRYPTION_KEY, API-Keys). Key bei Bedarf aus Vaultwarden holen und in .env eintragen; mittelfristig optional Anbindung (API/CLI) für ATLAS_CORE. Offene Punkte: [OFFENE_PUNKTE_AUDIT.md](OFFENE_PUNKTE_AUDIT.md).
- **Cursor/IDE:** Der Chat in Cursor verbraucht Cursor-eigene Quota; der **Dev-Agent** (Streamlit + Gemini/Claude) läuft außerhalb davon über deine Keys.
- **OpenClaw (Hostinger):** Siehe Abschnitt „Netzarchitektur: Messenger & OpenClaw“ oben; Anbindung an ATLAS optional. **VPS-Nutzung:** Welche Dienste zusätzlich auf dem Hostinger-Server sinnvoll sind (ChromaDB, Backup, ggf. leichtes Ollama) und wie OpenClaw in einer Sandbox betrieben wird: [VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md](VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md).

---

## Google Gemini APIs – Modellzuordnung (Stand 2026)

Bei einer **Paid API ohne Einschränkungen** werden die aktuellen **Pro-Modelle** genutzt; veraltete oder schwächere Modelle (z. B. Gemini 2.0 Flash, ältere Flash-Varianten) sind nicht vorgesehen. Referenz: [Gemini API Models](https://ai.google.dev/gemini-api/docs/models), [Pricing](https://ai.google.dev/gemini-api/docs/pricing). **Eigener Verbrauch / verfügbare Modelle:** [Gemin APITabelle (Google Sheets)](https://docs.google.com/spreadsheets/d/1RS8T7-Y3tDF0A0UdJL3LNZjbyVgsgySH7PUWaeMAzjs/edit?usp=sharing) (AI Studio – RPM, TPM, RPD pro Modell).

### Bildanalyse vs. Bildgenerierung (wichtig)

- **Bildanalyse** (Bild rein → Text raus: „Person sichtbar?“, „Zustand?“): Dafür sind **Textausgabemodelle mit Vision** zuständig – **Gemini 3.1 Pro**, **Gemini 3 Pro** (in der Tabelle unter „Textausgabemodelle“). Genau das nutzen wir für die Brio-Kamera.
- **Bildgenerierung / -bearbeitung** (Text/Bild rein → neues Bild raus): Dafür sind die **multimodalen generativen Modelle** zuständig – **Nano Banana** (Gemini 2.5 Flash Preview Image), **Nano Banana Pro (Gemini 3 Pro Image)**. Sie dienen der schnellen Bild**erzeugung**, nicht der Bild**auswertung**. Für „ist jemand zu sehen, welcher Zustand?“ also **nicht** Nano Banana (Pro) verwenden, sondern 3.1 Pro bzw. 3 Pro.

### Aktuelle Modelle (Auswahl, an Tabelle angelehnt)

| Modell (API-ID) | Kategorie (AI Studio) | Einsatz | Preis/Leistung | Geschwindigkeit | Qualität |
|-----------------|------------------------|---------|----------------|-----------------|----------|
| **gemini-3.1-pro-preview** | Textausgabemodelle | Dev-Agent, Heavy Reasoning, WhatsApp, **Brio-Bildauswertung** (Bild→Text) | Höher | Gut | Höchste; Reasoning, Multimodal |
| **gemini-3-pro-preview** (Gemini 3 Pro) | Textausgabemodelle | **Fallback** für 3.1 Pro (z. B. Brio, Heavy Reasoning) | Ähnlich Pro | Gut | Sehr hoch |
| **gemini-3-pro-image-preview** (Nano Banana Pro) | Multimodale generative Modelle | **Nur Bildgenerierung/-bearbeitung**, nicht Bildanalyse | Spezialisiert Bild-I/O | Mittel | Für Generierung |
| **gemini-2.5-pro** | Textausgabemodelle | Fallback; komplexe Aufgaben | Günstiger als 3.x | Etwas langsamer | Sehr gut |
| **gemini-3-flash-preview** | Textausgabemodelle | Hoher Durchsatz, Latenz-kritisch | Günstig | Sehr schnell | Gut |

**Hinweis:** Gemini 2.0 Flash und ältere Flash-Varianten sind deprecated und werden im Projekt nicht verwendet.

### Zuordnung zu ATLAS-Teilbereichen

| Teilbereich | Modell | Begründung |
|-------------|--------|------------|
| **Dev-Agent (Streamlit)** | `gemini-3.1-pro-preview` | Maximale Qualität; Paid API. |
| **WhatsApp: Text & Deep Reasoning** | `gemini-3.1-pro-preview` | Einheitliche Pro-Qualität. |
| **WhatsApp: Sprachnachricht (Transkript + Analyse)** | `gemini-3.1-pro-preview` | Multimodal (Audio). |
| **Brio-Kamera: Bildauswertung (Person, Zustand)** | `gemini-3.1-pro-preview`; Fallback `gemini-3-pro-preview` | Bildanalyse = Textausgabemodell mit Vision, **nicht** Nano Banana Pro (der ist für Generierung). |
| **LLM-Interface (Tier 5)** | `gemini-3.1-pro-preview`; Fallback `gemini-3-pro-preview` | Schwere kognitive Aufgaben. |
| **Triage** | Lokal (Ollama) oder optional `gemini-3-flash-preview` | Latenz kritisch. |

**.env-Variablen:** `GEMINI_DEV_AGENT_MODEL`, `GEMINI_HEAVY_MODEL`, `BRIO_VISION_MODEL` – Defaults siehe Code. Fallback für Vision/Heavy: `BRIO_VISION_MODEL=gemini-3-pro-preview` (Gemini 3 Pro), wenn 3.1 Pro nicht verfügbar ist.

---

## Skripte & Netzwerk-Referenzen (Übersicht)

| Bereich | Skript / Modul | Zweck |
|--------|----------------|-------|
| VPS-Setup | `src/scripts/setup_vps_hostinger.py` | Docker, Firewall, ChromaDB, OpenClaw, SOUL.md, Channels auf Hostinger |
| VPS-Check | `src/scripts/check_openclaw_vps.py` | OpenClaw-Container-Status und -Logs per SSH |
| VPS | `src/scripts/find_soul_on_vps.py` | Suche nach SOUL.md auf dem VPS |
| VPS | `src/scripts/test_vps_ssh.py` | SSH-Verbindungstest (VPS_HOST, VPS_USER, VPS_PASSWORD) |
| OpenClaw-Client | `src/network/openclaw_client.py` | Gateway-URL, Auth, `check_gateway()` |
| ChromaDB | `src/network/chroma_client.py` | Lokal/Remote-Client, Collections |
| ChromaDB | `src/scripts/ingest_nd_insights_to_chroma.py` | ND-Insights in ChromaDB einspielen |
| Kamera | `src/network/go2rtc_client.py` | Snapshot-URL, `get_snapshot()` (go2rtc oder CAMERA_SNAPSHOT_URL) |
| Kamera | `src/scripts/test_go2rtc_snapshot.py` | Snapshot-Test, speichert in `data/media/` |
| Kamera | `src/scripts/camera_snapshot_server.py` | On-Demand-Snapshot-Server für Webcam (Brio nur bei Abruf aktiv) |
| Kamera | `src/scripts/brio_scenario_periodic.py` | Brio-Szenario: alle 1 min Bild → Auswertung (Person, Zustand) → Protokoll; bei Bedarf mehrere Bilder |
| Kamera | `src/scripts/tapo_garden_recognize.py` | Tapo (Balkon): Frame holen (TAPO_FRAME_URL/RTSP), speichern, optional Gemini-Erkennung; FFmpeg aus driver/go2rtc_win64 |
| Kamera | `src/ai/brio_image_analyzer.py` | Gemini Vision: Person sichtbar?, STATE, NEED_MORE für Brio-Szenario |

---
*Stand: Projekt-Dokumentation ATLAS_CORE. Voice/UI siehe ATLAS_VOICE_ARCHITECTURE_V1.3.md. Netzarchitektur: siehe Abschnitt „Netzarchitektur“ sowie VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md.*

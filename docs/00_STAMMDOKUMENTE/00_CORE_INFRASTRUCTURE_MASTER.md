<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE INFRASTRUCTURE MASTER PLAN

**Generiert am:** 2026-03-06 11:09:15

![CORE Visual Context](../../CORE.png)

---

## Inhaltsverzeichnis

- [ADGUARD HOME SETUP](#adguard-home-setup)
- [BACKUP PLAN](#backup-plan)
- [BACKUP PLAN FINAL](#backup-plan-final)
- [CAMERA GO2RTC WINDOWS](#camera-go2rtc-windows)
- [CUSTOM WAKE WORD CORE](#custom-wake-word-core)
- [CUSTOM WAKE WORD TRAINING](#custom-wake-word-training)
- [FRITZBOX ADGUARD ZERTIFIKAT](#fritzbox-adguard-zertifikat)
- [FRITZBOX NETZWERK CONFIG](#fritzbox-netzwerk-config)
- [HA SCOUT MX INTEGRATION](#ha-scout-mx-integration)
- [MTLS MIGRATION PLAN](#mtls-migration-plan)
- [MX KAMERA CORE HOEREN SEHEN](#mx-kamera-core-hoeren-sehen)
- [OC BRAIN LEERE NACHRICHTEN DIAGNOSE](#oc-brain-leere-nachrichten-diagnose)
- [OPENWAKEWORD MODELS](#openwakeword-models)
- [SCOUT ASSIST PIPELINE](#scout-assist-pipeline)
- [SCOUT GO2RTC CONFIG](#scout-go2rtc-config)
- [SCOUT HA EVENT AN OC BRAIN](#scout-ha-event-an-oc-brain)
- [SCOUT USB KAMERA MIKRO HA OS](#scout-usb-kamera-mikro-ha-os)
- [SCOUT WAKE WORD SETUP](#scout-wake-word-setup)
- [TAMPERMONKEY TTS INTEGRATION](#tampermonkey-tts-integration)
- [VOICE PIPELINE AUDIO INPUT PLAN](#voice-pipeline-audio-input-plan)
- [VPS DIENSTE UND OPENCLAW SANDBOX](#vps-dienste-und-openclaw-sandbox)
- [VPS FULL STACK SETUP](#vps-full-stack-setup)
- [VPS IP MONITORING](#vps-ip-monitoring)
- [VPS SLIM DEPLOY](#vps-slim-deploy)
- [WHATSAPP E2E HA SETUP](#whatsapp-e2e-ha-setup)
- [google assistant ollama research](#google-assistant-ollama-research)
- [usb microphone research](#usb-microphone-research)

---


<a name="adguard-home-setup"></a>
# ADGUARD HOME SETUP

## AdGuard Home - DNS Server (Scout)

### Überblick
- Rolle: Zentraler DNS-Server für das LAN (Pi-hole-Ersatz)
- Läuft als HA-Addon auf Scout (192.168.178.54)
- Addon-Slug: `a0d7b954_adguard`, Version: v0.107.72
- Web UI: http://192.168.178.54:3000
- `leave_front_door_open` ist aktiv (kein Login für API)

### Installation (HA Addon)
1. HA Web UI → Einstellungen → Add-ons → Add-on Store
2. "AdGuard Home" suchen → Installieren
3. Konfiguration Tab:
   - SSL: an (fullchain.pem / privkey.pem)
   - Port 53 (DNS) auf Host exponiert
   - Port 3000 (Web UI) → 80/tcp
4. Starten

### DNS-Konfiguration
- Upstream DNS: `1.1.1.1`, `8.8.8.8`, `9.9.9.9`
- Bootstrap DNS: `1.1.1.1`, `8.8.8.8`
- Protection: aktiviert

### DNS-Rewrites
| Domain | Antwort | Zweck |
|--------|---------|-------|
| mth-home2go.duckdns.org | 192.168.178.54 | HA lokal auflösbar |
| api.govee.com | *.api.govee.com | Govee-Geräte |

### DHCP-Server
AdGuard DHCP ist aktiviert (parallel zur FritzBox):
- Interface: `end0`
- Range: 192.168.178.20 - 192.168.178.199
- Gateway: 192.168.178.1
- Statische Leases für alle Google/Nest-Geräte eingerichtet

**Wichtig:** FritzBox DHCP läuft parallel. Die FritzBox gibt per DHCPv6 immer sich selbst als DNS aus. Google Minis bevorzugen IPv6-DNS und umgehen damit AdGuard.

### FritzBox-Konfiguration
- Internet → Zugangsdaten → DNS-Server:
  - DNSv4: 192.168.178.54 (AdGuard), Fallback: 1.1.1.1
  - DNSv6: fd8d:4ce:b6e8:0:2a5a:f9e5:c0bd:455c (Scout ULA)
- Heimnetz → Netzwerk → IPv4: Lokaler DNS = 192.168.178.54
- Heimnetz → Netzwerk → IPv6: DNSv6-Server im Heimnetz = Scout ULA

**Bekannte Einschränkung:** Die FritzBox 7583 gibt per DHCPv6 trotzdem sich selbst als DNS aus. Google Minis fragen daher die FritzBox statt AdGuard. Siehe TTS-Fix unten.

### TTS auf Google Minis -- Die Lösung

**Problem:** Google Minis bekommen TTS-Audio-URLs von HA. Wenn die URL `https://mth-home2go.duckdns.org/...` enthält und die Minis die Domain auf die externe IP auflösen (weil sie den FritzBox-DNS nutzen), können sie das Audio nicht laden (SSL-Zertifikat passt nicht / Server nicht erreichbar).

**Lösung:** HA `external_url` auf die lokale IP setzen:
```
external_url: https://192.168.178.54:8123
internal_url: http://192.168.178.54:8123
```
HA erkennt, dass Cast-Geräte die lokale HTTPS-URL nicht mit gültigem Zertifikat laden können, und routet die TTS-Audio-URLs automatisch über **Nabu Casa Cloud** (`*.ui.nabu.casa`). Nabu Casa hat gültige öffentliche SSL-Zertifikate, die die Minis akzeptieren.

**Gesetzt via:** WebSocket API `config/core/update`

### Verifizierung
```bash
## AdGuard DNS-Rewrite prüfen
nslookup mth-home2go.duckdns.org 192.168.178.54
## Erwartetes Ergebnis: 192.168.178.54

## TTS-Test
## TTS-URLs sollten über nabu.casa geroutet werden:
## https://5fggbz3aeugcmhkxm9egldv4fw3dgplh.ui.nabu.casa/api/tts_proxy/...
```

### Blocklisten (Pi-hole-Ersatz)
- Standard-Blockliste von AdGuard (vorinstalliert)
- Optional: Steven Black Unified Hosts
- Optional: OISD Full

### Status
- [x] Addon installiert und gestartet
- [x] DNS-Upstream konfiguriert (1.1.1.1, 8.8.8.8, 9.9.9.9)
- [x] DNS-Rewrite für DuckDNS aktiv
- [x] FritzBox DNS umgestellt (v4 + v6)
- [x] DHCP mit statischen Leases für Google-Geräte
- [x] TTS funktioniert auf Google Minis (via Nabu Casa Routing)
- [x] Google TTS verifiziert (2026-03-01)
- [x] ElevenLabs TTS verifiziert (2026-03-01)


---


<a name="backup-plan"></a>
# BACKUP PLAN

## Täglicher Backup-Plan

### 1. Ziel
Sicherstellung der Datenintegrität und -verfügbarkeit durch automatisierte tägliche Backups aller kritischen Projektdaten.

### 2. Was wird gesichert?
- **Anwendungscode:** Das gesamte Projektverzeichnis (exklusive temporärer Dateien, `node_modules`, `.git`, etc.).
- **Datenbank:** Vollständiger Dump der primären Datenbank (z.B. PostgreSQL, MySQL, SQLite für CORE).
- **Konfigurationsdateien:** `.env`, `config/` Verzeichnis.
- **(Optional) Benutzerdaten/Uploads:** Spezifisches Verzeichnis, falls vorhanden (z.B. `media/`, `uploads/`).

### 3. Wohin wird gesichert?
- **Primär:** Lokaler Backup-Speicher auf dem Server (z.B. `/var/backups/projektname/` bzw. unter Windows ein dediziertes Laufwerk/Ordner).
- **Sekundär:** Externer Cloud-Speicher (z.B. S3-Bucket, Google Cloud Storage) für Offsite-Sicherung.

### 4. Wie wird gesichert? (Automatisierung)
Ein Python-Skript (`scripts/daily_backup.py`) wird erstellt, das folgende Schritte automatisiert:

1. **Datenbank-Dump erstellen** (Beispiel SQLite für CORE):
   - `data/shell_db/`, `*.sqlite` in ein zeitgestempeltes Archiv.

2. **Anwendungscode/Konfiguration archivieren:**
   - Projekt-Root als tar.gz/zip, exkl. `node_modules`, `.git`, `__pycache__`, virtuelle Umgebungen.

3. **Upload zu Cloud-Speicher (optional):** z.B. boto3 für S3.

4. **Retention:** Lokale und Cloud-Backups älter als Aufbewahrungsfrist löschen.

### 5. Wann wird gesichert?
- **Zeitpunkt:** Täglich um 03:00 Uhr UTC (oder Off-Peak-Zeit).
- **Scheduler:** `cron` (Linux) oder Task Scheduler (Windows).

### 6. Aufbewahrungsrichtlinie (Retention)
- Die letzten 7 täglichen Backups werden aufbewahrt.

### 7. Überwachung & Benachrichtigung
- Protokollierung in Log-Datei; bei Fehlern E-Mail oder Slack.

### 8. Wiederherstellungstest
- Mindestens einmal pro Monat vollständiger Wiederherstellungstest auf Staging.

---
*Quelle: Projekt-Plan.*


---


<a name="backup-plan-final"></a>
# BACKUP PLAN FINAL

## Backup-Plan (final) – CORE

**Einziges Backup-Ziel: Hostinger-VPS** (`/var/backups/core`). Kein lokales Primärziel, kein S3 – alles geht per Push vom Rechner (4D_RESONATOR (CORE)) zum VPS.

---

### 1. Ziel

Kritische Projektdaten (Code, Konfiguration, SQLite-DB) täglich automatisiert auf dem Hostinger-VPS sichern. ChromaDB liegt auf dem VPS und wird dort separat gesichert (siehe Abschnitt 5).

### 2. Was wird gesichert?

| Inhalt | Quelle | Anmerkung |
|--------|--------|-----------|
| Anwendungscode | Projekt-Root | Ausschlüsse: `.git`, `__pycache__`, `node_modules`, `*.pyc`, venv, `data/backups`, `logs` |
| Konfiguration | `config/` | Vollständig |
| .env | Projekt-Root | **Nur verschlüsselt** (Fernet); Schlüssel nicht im Backup |
| SQLite-DB | `data/shell_db/*.sqlite` | Vollständig |

ChromaDB-Daten liegen auf dem VPS; Backup der ChromaDB erfolgt auf dem VPS (Cold-Backup, siehe Abschnitt 5).

### 3. Wohin?

- **Ziel:** Hostinger-VPS, Verzeichnis `/var/backups/core`
- **Transport:** Push per SSH/SFTP (Paramiko) von 4D_RESONATOR (CORE) aus; der VPS pullt nicht.
- **Berechtigung:** `/var/backups/core` wird von `setup_vps_hostinger.py` mit `chmod 700` angelegt (bereits vorhanden).

### 4. Wie wird gesichert? (Automatisierung)

- **Automatisiertes Backup:** Ein Windows Task führt `python src/scripts/daily_backup.py` täglich aus (seit 25.02.2026 aktiv). Das Skript packt den Code (ohne `node_modules`, `.venv` etc.) und lädt ihn per SFTP auf den Hostinger-VPS in `/var/backups/core`.
  - Erstellt ein Archiv (tar.gz) aus Code, `config/`, `data/shell_db/`.
  - `.env` wird bei gesetztem `BACKUP_ENCRYPTION_KEY` mit Fernet verschlüsselt und als separate Datei hochgeladen.
  - Upload per SFTP zu `VPS_HOST` mit `VPS_USER` / `VPS_PASSWORD` aus `.env`.
  - **Retention:** Auf dem VPS werden Backups älter als 7 Tage gelöscht (vom Skript per SSH-Befehl ausgeführt).
- **Logging:** `logs/backup.log` (im Projekt); bei Fehlern Eintrag mit Fehlermeldung.
- **Optional:** `HEALTHCHECK_URL` (z. B. healthchecks.io) für erfolgreichen Lauf pingen.

### 5. ChromaDB-Backup (auf dem VPS)

ChromaDB läuft im Container auf dem VPS. Ein Cold-Backup (Container kurz stoppen → Verzeichnis sichern → starten) wird über ein auf dem VPS hinterlegtes Skript und Cron erledigt. Siehe `docs/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md` (Backup-Ziel) und optional `chroma_backup.sh` (Bereitstellung über `setup_vps_hostinger.py`).

### 6. Wann? (Automatisierung)

- **Zeitpunkt:** Täglich, z. B. 04:00 Uhr (Windows: Task Scheduler; Linux: cron).
- **Windows (Task Scheduler):**
  - **Programm:** `C:\CORE\scripts\run_daily_backup.bat`  
  - **Arbeitsverzeichnis:** `C:\CORE`  
  - Oder direkt: Programm `python`, Argument `C:\CORE\src\scripts\daily_backup.py`, Starten in `C:\CORE`.
- **Linux (cron):**  
  `0 4 * * * cd /pfad/zu/CORE && python3 src/scripts/daily_backup.py >> logs/backup.log 2>&1`
- **Windows Task Scheduler (einmalig anlegen):**  
  Als Administrator in cmd/PowerShell:  
  `schtasks /create /tn "CORE Daily Backup" /tr "C:\CORE\scripts\run_daily_backup.bat" /sc daily /st 04:00 /ru SYSTEM`  
  (Oder GUI: Aufgabenplanung → Aufgabe erstellen → Trigger täglich 04:00, Aktion: Batch-Datei oder `python …\daily_backup.py`.)

### 7. Aufbewahrung (Retention)

- Die letzten **7** täglichen Backups werden auf dem VPS behalten; ältere werden von `daily_backup.py` beim Upload entfernt.

### 8. Wiederherstellung

- Archiv von `/var/backups/core` per SCP/SFTP zurück auf den Rechner, entpacken.
- Falls `.env.enc` gesichert wurde: mit dem gleichen `BACKUP_ENCRYPTION_KEY` entschlüsseln (Fernet).
- **Restore-Test:** Mindestens einmal pro Monat auf Testordner/Staging prüfen.

### 9. Konfiguration (.env)

| Variable | Bedeutung |
|----------|-----------|
| `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` | Bereits vorhanden; werden für Backup-Upload genutzt. |
| `BACKUP_ENCRYPTION_KEY` | Optional. Gültiger Fernet-Key (z. B. aus `Fernet.generate_key().decode()`); wenn gesetzt, wird `.env` verschlüsselt als `.env.enc` ins Archiv aufgenommen. **Empfohlen:** Key in Vaultwarden (Scout) ablegen und bei Bedarf in .env eintragen. |
| `BACKUP_RETENTION_DAYS` | Optional, Standard 7. |
| `HEALTHCHECK_URL` | Optional; URL wird bei Erfolg per GET aufgerufen (z. B. healthchecks.io). |

---

*Konsolidiert aus BACKUP_PLAN.md und Audit-Anmerkungen. Einzige Referenz für Backup-Ziel und -Ablauf.*


---


<a name="camera-go2rtc-windows"></a>
# CAMERA GO2RTC WINDOWS

## Kamera-Anbindung: go2rtc (Windows / Scout)

CORE kann Kamerabilder über go2rtc beziehen. go2rtc läuft entweder **auf dem PC** (Windows, z.B. Logitech Brio) oder **auf dem Scout (Pi)** – letzteres ist oft stabiler.

---

### Webcam vs. Überwachungskamera (warum die Brio „nicht immer läuft“)

- **Überwachungs-/IP-Kamera:** Läuft dauerhaft, streamt 24/7, LED oft dauerhaft an. Typisch für go2rtc auf dem **Scout** (Pi-Kamera oder USB-Kamera am Pi).
- **Webcam (z.B. Logitech Brio):** Ist für **On-Demand** ausgelegt – sie überträgt nur, wenn eine Anwendung sie explizit anspricht und Frames anfordert. Dauerstream ist nicht das typische Nutzungsprofil; die LED bleibt oft aus, wenn kein Programm die Kamera hält.

Für CORE reicht in der Regel **ein Snapshot bei Bedarf** (z.B. ein Bild pro Anfrage). Dafür muss die Kamera nicht dauerhaft laufen. Zwei Wege:

1. **go2rtc (PC oder Scout):** Wenn ein Stream konfiguriert ist, liefert die Snapshot-API (`/api/frame.jpeg?src=...`) bei jedem Aufruf ein aktuelles Bild – go2rtc hält dabei ggf. den Stream kurz an. Beim Scout ist der Stream oft dauerhaft aktiv (Kamera am Pi); am PC mit Brio kann der Stream bei reiner On-Demand-Nutzung zwischen den Abrufen ruhen oder über einen **On-Demand-Snapshot-Server** (siehe unten) abgedeckt werden.
2. **On-Demand-Snapshot-Server (nur Brio/PC):** Ein kleiner Dienst, der **nur bei einem HTTP-Aufruf** (z.B. GET /snapshot.jpg) die Webcam kurz öffnet, ein Einzelbild liefert und wieder schließt – LED nur während des Abrufs. Siehe Abschnitt „On-Demand-Snapshot für die Brio (PC)“.

#### MX (Brio) als Überwachungskamera: Dauerstream

Wenn du die Brio **wie eine Überwachungskamera** nutzen willst (ständig Bild für Erkennung/Brio-Szenario), ist es **kein Problem**, den Stream **dauerhaft laufen zu lassen**. Du kannst go2rtc mit dem Brio-Stream einfach durchlaufen lassen – die Kamera bleibt dann aktiv (LED an), und CORE (z.B. `brio_scenario_periodic.py` oder Snapshot-Abfragen) bekommt jederzeit ein aktuelles Bild. Ein gezieltes An- und Abschalten ist nicht nötig; wenn du den Dauerbetrieb möchtest, starte go2rtc mit der Brio-Konfiguration und lasse ihn laufen. Siehe Abschnitt „Logitech Brio (MX) unter Windows einbinden“ für die go2rtc-Einrichtung.

---

### Alternative: go2rtc auf dem Scout (empfohlen, wenn PC-Stream Probleme macht)

Auf dem **Scout (Raspberry Pi)** läuft go2rtc bereits und funktioniert ohne Probleme. Statt die Brio am PC zu nutzen, kannst du den Kamera-Stream **über den Scout** abgreifen:

1. **Scout-IP oder Hostname** ermitteln (z.B. `192.168.2.x` oder `scout.local`).
2. In der **CORE .env** setzen:
   - `GO2RTC_BASE_URL=http://<scout-ip>:1984` (z.B. `http://192.168.2.10:1984` oder `http://scout.local:1984`)
   - `GO2RTC_STREAM_NAME=<name>` – genau der Stream-Name, der auf dem Scout in go2rtc angelegt ist (z.B. `pc`, `cam`, `camera`).
3. Test: `python src/scripts/test_go2rtc_snapshot.py` – sollte ein Snapshot vom Scout-Stream liefern.

Damit nutzt CORE den gleichen `go2rtc_client` und dieselbe Snapshot-API, nur gegen die Scout-Instanz. Kein weiterer Code nötig.

---

### Logitech Brio (MX / 4K) unter Windows einbinden

Diese Anleitung beschreibt, wie eine Logitech Brio Kamera in `go2rtc` **auf dem PC** unter Windows eingebunden wird.

### Voraussetzungen

- **FFmpeg:** Die Skripte (Brio Snapshot-Server, Tapo RTSP/MP4) nutzen **zuerst** `driver/go2rtc_win64/ffmpeg.exe` und setzen das Arbeitsverzeichnis auf diesen Ordner (damit DLLs zuverlässig gefunden werden). So entstehen keine Konflikte mit anderem FFmpeg im PATH. Optional: System-FFmpeg (z.B. `winget install Gyan.FFmpeg`) und in .env `FFMPEG_PATH` setzen.
- **go2rtc**: Die `go2rtc.exe` befindet sich im gleichen Verzeichnis wie FFmpeg.

### Schritt 1 – Kameraname ermitteln

Um den exakten Namen der Kamera für FFmpeg zu finden, führe folgenden Befehl aus:

```powershell
& "C:\CORE\driver\go2rtc_win64\ffmpeg.exe" -list_devices true -f dshow -i dummy
```

Suche unter der Sektion „DirectShow video devices“ nach dem Namen deiner Kamera (z. B. `"Logitech BRIO"` oder `"Logitech BRIO 4K"`). Notiere dir diesen Namen exakt.

Alternativ kannst du die Datei `list_dshow_cameras.bat` im `driver/go2rtc_win64/`-Ordner ausführen.

### Schritt 2 – Stream anlegen

#### Über die Web-UI
1. Öffne die go2rtc Web-UI unter [http://localhost:1984](http://localhost:1984).
2. Klicke auf **Streams** und dann auf **Add stream**.
3. **Name**: z. B. `pc`
4. **Source**:
   ```text
   exec:ffmpeg -f dshow -video_size 1920x1080 -framerate 30 -i video="Logitech BRIO" -c:v libx264 -preset ultrafast -f mpegts -
   ```
   *(Ersetze `"Logitech BRIO"` durch deinen notierten Namen)*

#### Über die Config-Datei (go2rtc.yaml)
Erstelle eine `go2rtc.yaml` im Ordner `driver/go2rtc_win64/` mit folgendem Inhalt:

```yaml
streams:
  pc: exec:ffmpeg -f dshow -video_size 1920x1080 -framerate 30 -i video="Logitech BRIO" -c:v libx264 -preset ultrafast -f mpegts -
```

### Schritt 3 – Auflösung anpassen (Optional)

Für 4K Auflösung ändere den Parameter `-video_size`:
- **4K**: `-video_size 3840x2160`
- **Full HD**: `-video_size 1920x1080`

### Schritt 4 – Funktionstest

Führe das Test-Script aus, um zu prüfen, ob ein Snapshot erstellt werden kann:

```powershell
python src/scripts/test_go2rtc_snapshot.py
```

---

### On-Demand-Snapshot für die Brio (PC)

Wenn die Brio **nur bei Bedarf** ein Bild liefern soll (kein Dauerstream, LED nur beim Abruf an), kannst du den **On-Demand-Snapshot-Server** nutzen:

- **Skript:** `src/scripts/camera_snapshot_server.py` (startet einen kleinen HTTP-Server; bei jedem GET auf `/snapshot.jpg` wird einmal FFmpeg ausgeführt, ein Einzelbild von der Brio gelesen und zurückgegeben).
- **Voraussetzung:** FFmpeg aus `driver/go2rtc_win64/` (Skript setzt cwd dort); Kameraname in .env `CAMERA_DEVICE_NAME` (z.B. `Logitech BRIO`).
- **.env:** Optional `CAMERA_SNAPSHOT_URL=http://localhost:8555/snapshot.jpg` setzen. Der `go2rtc_client` nutzt dann diese URL für MX-Abfragen (Snapshot = On-Demand-Aktivierung der Webcam).
- **Stabiler Ablauf:** Für MX-Tests oder Brio-Szenario den **Snapshot-Server vorher starten** (in einem eigenen Terminal: `python src/scripts/camera_snapshot_server.py`), danach z.B. `python src/scripts/mx_save_images_only.py` oder `brio_scenario_periodic.py`. Alternativ go2rtc mit Brio-Stream laufen lassen und `CAMERA_SNAPSHOT_URL` leer lassen (dann wird go2rtc genutzt).

So bleibt die Webcam im Alltag aus und wird nur bei einem Aufruf kurz aktiviert.

---

### Tapo (Balkon): Erkennungstest in den Garten

Die **Tapo-Kamera** am Balkon eignet sich für den Erkennungstest, weil sie dauerhaft läuft – der Bildbezug ist damit von vornherein stabil. **Wichtig:** Der Test geht **in den Garten** (Bereich Mülltonnen, wo genug Leute vorbeilaufen), **nicht** durchs Fenster in die Wohnung (zu viele Spiegelungen).

**go2rtc-Streams (Beispiel HA-Config):** Typische Stream-Namen sind z. B. **Balkon_HD** (Tapo) und **DCS6100** (andere Kamera). Die Quelle für Balkon_HD ist der RTSP-Stream der Tapo; go2rtc stellt dann u. a. `frame.mp4` und **`frame.jpeg`** bereit.

**Einzelbild-Quelle:** go2rtc liefert den Frame über die HTTP-API. Über HA hassio_ingress z. B.  
- **frame.jpeg** (empfohlen): direkt JPEG, keine Extraktion nötig  
  `https://home:8123/api/hassio_ingress/<TOKEN>/api/frame.jpeg?src=Balkon_HD`  
- **frame.mp4**:  
  `https://home:8123/api/hassio_ingress/<TOKEN>/api/frame.mp4?src=rtsp://home:8554/Balkon_HD?mp4`  

→ in .env **`TAPO_FRAME_URL`** setzen (mit deinem Token). Bei **frame.jpeg** liefert das Skript sofort ein JPEG; bei frame.mp4 wird ein Frame per FFmpeg extrahiert. Bei 401 (Ingress-Auth) nutzt das Skript automatisch **`TAPO_RTSP_URL`** (z. B. `rtsp://<Scout-IP>:8554/Balkon_HD`); dafür braucht der PC FFmpeg. Wenn FFmpeg auf dem PC abbricht (z. B. DLL fehlt), **frame.jpeg** über Ingress nutzen oder Ingress-Token prüfen.  
Skript: `python src/scripts/tapo_garden_recognize.py` (Frame → `data/tapo_garden/` + optional Erkennung).

---

### Brio-Szenario: periodische Auswertung (Person + Zustand, Protokoll)

Damit CORE **zur Laufzeit** erkennen kann, ob etwas nicht stimmt (Anwesenheit, Auffälligkeiten), muss **mindestens einmal pro Minute** ein Bild ausgewertet werden – ein Intervall von 50 Minuten wäre für solche Zwecke wertlos (z.B. Erkennung von Notfällen). Für den ersten Test kannst du das Intervall per .env auf 50 min stellen; für den eigentlichen Betrieb ist **1× pro Minute** der sinnvolle Standard.

- **Skript:** `python src/scripts/brio_scenario_periodic.py`  
  - **Standard:** alle **1 Minute** ein Zyklus, **60 Minuten** lang (also 60 Zyklen).  
  - Ein Zyklus: 1 Snapshot → Gemini Vision (Person ja/nein, STATE, NEED_MORE) → bei NEED_MORE bis zu 5 weitere Snapshots → erneute Auswertung → Eintrag ins Protokoll.
- **Einmaliger Test:** `python src/scripts/brio_scenario_periodic.py once`
- **Protokoll:** `data/brio_scenario/protocol.jsonl` (eine Zeile pro Zyklus, JSON mit `ts`, `person_visible`, `state`, `images_used`, `image_paths`).
- **Bilder** werden unter `data/brio_scenario/` abgelegt (`brio_*.jpg`, ggf. `brio_extra_*.jpg`).
- **.env (optional):** `BRIO_SCENARIO_INTERVAL_MIN=1` (Standard: 1 min; für ersten Test z.B. `50`), `BRIO_SCENARIO_DURATION_MIN=60`, `BRIO_SCENARIO_MAX_EXTRA=5`, `BRIO_SCENARIO_LOG_DIR`, `BRIO_VISION_MODEL=gemini-3.1-pro-preview`. Kamera wie gewohnt (GO2RTC_* oder CAMERA_SNAPSHOT_URL); für Vision wird `GEMINI_API_KEY` benötigt.


---


<a name="custom-wake-word-core"></a>
# CUSTOM WAKE WORD CORE

﻿# Custom Wake Word: CORE

Anleitung zum Erstellen eines Custom Wake Words "CORE" fuer openWakeWord in Home Assistant.

---

### 1. Aktueller Stand

| Eigenschaft | Wert |
|-------------|------|
| **Wake Word Entity** | `wake_word.openwakeword` |
| **Pipeline** | CORE (ID: `01hzktez4kncsm0sr1qx32hy5x`) |
| **Aktuelles Wake Word** | `hey_jarvis_v0.1` |
| **openWakeWord Host** | `core-openwakeword:10400` |

---

### 2. Verfuegbare Standard Wake Word Models

openWakeWord bietet folgende **vorgefertigte Models** an:

| Model | Beschreibung | Verfuegbarkeit |
|-------|--------------|----------------|
| `ok_nabu` | "Ok Nabu" - Home Assistant default | Standard |
| `hey_nabu` | "Hey Nabu" | Standard |
| `hey_jarvis_v0.1` | "Hey Jarvis" (Star Trek/Iron Man Style) | **Aktuell aktiv** |
| `hey_mycroft` | "Hey Mycroft" (Mycroft AI) | Standard |
| `alexa` | "Alexa" (Amazon Style) | Standard |
| `hey_rhasspy` | "Hey Rhasspy" | Standard |

#### Community Wake Word Models

Von [fwartner/home-assistant-wakewords-collection](https://github.com/fwartner/home-assistant-wakewords-collection):

| Model | Beschreibung | Accuracy | Download |
|-------|--------------|----------|----------|
| `computer_v2` | "Computer" / "Hey Computer" (Star Trek LCARS) | 78.3% | [Link](https://github.com/fwartner/home-assistant-wakewords-collection/tree/main/en/computer) |
| `hal` | "HAL" (2001 Space Odyssey) | - | [Link](https://github.com/fwartner/home-assistant-wakewords-collection/tree/main/en/hal) |
| `hey_jarvis` | "Hey Jarvis" | - | Community |
| `glados` | "GLaDOS" (Portal) | - | Community |

---

### 3. "Computer" Wake Word JETZT aktivieren

Das `computer_v2.tflite` Model wurde bereits heruntergeladen und auf Scout kopiert.

**Speicherort auf Scout:** `/share/openwakeword/computer_v2.tflite`

#### 3.1 openWakeWord Add-on konfigurieren

1. **HA Web-UI oeffnen:** https://192.168.178.54:8123
2. **Navigation:** Einstellungen > Add-ons > openWakeWord > Konfiguration
3. **Custom Model Pfad hinzufuegen:**
   `yaml
   custom_model_dir: /share/openwakeword
   `
4. **Add-on neustarten**

#### 3.2 Pipeline Wake Word aendern

Nach Add-on Neustart erscheint `computer_v2` in der Wake Word Auswahl:

1. **Navigation:** Einstellungen > Voice assistants > CORE > Wake word
2. **Auswahl:** `computer_v2` aus der Liste waehlen
3. **Speichern**

#### 3.3 Alternativ: Direkt in Storage-Datei

Editiere `S:\.storage\assist_pipeline.pipelines`:

`json
{
  "wake_word_entity": "wake_word.openwakeword",
  "wake_word_id": "computer_v2"
}
`

Nach Aenderung HA neustarten.

---

### 4. Custom Wake Word "CORE" trainieren

#### 4.1 Voraussetzungen

- Python 3.9+ mit pip
- Audio-Aufnahmen des Wake Words (min. 50-100 Samples empfohlen)
- Negativ-Samples (Sprache ohne Wake Word)

#### 4.2 openWakeWord Training Repository

`bash
git clone https://github.com/dscripka/openWakeWord
cd openWakeWord
pip install -e .[training]
`

#### 4.3 Daten-Struktur erstellen

`
training_data/
+-- positive/
|   +-- mtho_001.wav
|   +-- mtho_002.wav
|   +-- ... (min. 50 Aufnahmen von "CORE")
+-- negative/
    +-- random_speech_001.wav
    +-- ... (Hintergrund/andere Sprache)
`

**Audio-Anforderungen:**
- Format: WAV, 16kHz, Mono, 16-bit
- Laenge: 1-3 Sekunden pro Sample
- Verschiedene Sprecher und Umgebungen empfohlen

#### 4.4 Training durchfuehren

`python
from openwakeword import train

config = {
    "target_phrase": "core",
    "positive_audio_dir": "training_data/positive",
    "negative_audio_dir": "training_data/negative",
    "output_dir": "models/core",
    "epochs": 100,
    "batch_size": 32
}

train.train_model(**config)
`

**Alternative: Web-basiertes Training**
https://www.home-assistant.io/voice_control/create_wake_word/

#### 4.5 Model deployen

`bash
## Model nach Scout kopieren
copy models\core\core_v1.tflite S:\share\openwakeword\
`

---

### 5. Installierte Models (lokal)

| Datei | Groesse | Beschreibung |
|-------|---------|--------------|
| `hey_jarvis_v0.1.tflite` | 1.2 MB | Standard Jarvis Model |
| `computer_v2.tflite` | 207 KB | Star Trek "Computer" |

Speicherort auf 4D_RESONATOR (CORE): `c:\CORE\data\openwakeword_models\`
Speicherort auf Scout: `/share/openwakeword/`

---

### 6. Naechste Schritte

| Schritt | Beschreibung | Status |
|---------|--------------|--------|
| 1 | "computer" Model auf Scout kopiert | ERLEDIGT |
| 2 | openWakeWord Custom Model Pfad konfigurieren | **MANUELL** |
| 3 | Pipeline auf "computer_v2" umstellen | **MANUELL** |
| 4 | CORE Wake Word Samples aufnehmen | Ausstehend |
| 5 | CORE Custom Training durchfuehren | Ausstehend |

---

### 7. Referenzen

- [openWakeWord GitHub](https://github.com/dscripka/openWakeWord)
- [Home Assistant Wake Words](https://www.home-assistant.io/voice_control/create_wake_word/)
- [Community Wake Word Collection](https://github.com/fwartner/home-assistant-wakewords-collection)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [LCARS Star Trek Computer](https://en.wikipedia.org/wiki/LCARS)

---

*Erstellt: 2026-03-04*
*Pipeline: CORE (01hzktez4kncsm0sr1qx32hy5x)*


---


<a name="custom-wake-word-training"></a>
# CUSTOM WAKE WORD TRAINING

## Custom Wake Word Training – „hey core“ und „computer“

**Zweck:** Anleitung zum Trainieren eigener openWakeWord-Modelle für CORE und Computer.

---

### 1. Google Colab – Wake Word Training

#### 1.1 Link

**[Wake Word Training Environment](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing)**

#### 1.2 Voraussetzungen

- Google-Konto
- Browser-Tab während des Trainings offen lassen (~30–60 Min.)
- Aktuell nur englische Wake Words unterstützt (Aussprache wird per Piper TTS generiert)

---

### 2. Schritte für „hey core“

1. **Colab öffnen:** Link oben → „Datei → Eine Kopie erstellen“ (eigene Kopie anlegen)
2. **target_word setzen:** In Sektion 1 `target_word = "hey core"` (oder `"core"` für kürzeres Wort)
3. **Aussprache prüfen:** Play-Button neben `target_word` klicken → Audio anhören
4. **Rechtschreibung anpassen:** Falls nötig, Schreibweise ändern (z.B. „hey core“ vs. „hey atläs“ für deutsche Aussprache)
5. **Runtime → Run all** ausführen
6. **Warten:** Ca. 30–60 Minuten (Colab-Ressourcen abhängig)
7. **Download:** `.tflite`-Datei aus dem Output herunterladen
8. **Dateiname:** z.B. `hey_core_v0.1.tflite` (Colab generiert den Namen)

#### 2.1 Ablage auf Scout

- Samba: `\\192.168.178.54\share\openwakeword\`
- Oder: `scripts/setup_scout_wake_words.py` (siehe unten)
- Datei: `hey_core_v0.1.tflite` nach `/share/openwakeword/` kopieren

---

### 3. Schritte für „computer“

1. **Colab öffnen:** Gleicher Link wie oben
2. **target_word setzen:** `target_word = "computer"`
3. **Aussprache prüfen:** Play-Button → Audio anhören (englische Aussprache)
4. **Runtime → Run all** ausführen
5. **Warten:** Ca. 30–60 Minuten
6. **Download:** `.tflite`-Datei (z.B. `computer_v0.1.tflite`)
7. **Ablage:** Nach `/share/openwakeword/` auf Scout kopieren

---

### 4. Ablage auf Scout – Verzeichnis

| Pfad (Scout/HA)      | Beschreibung                          |
|----------------------|---------------------------------------|
| `/share/openwakeword`| Verzeichnis für Custom Wake Word Modelle |

**Namenskonvention:** `{wakeword}_v{version}.tflite` (z.B. `hey_core_v0.1.tflite`, `computer_v0.1.tflite`)

Das openWakeWord Add-on scannt dieses Verzeichnis automatisch. Nach dem Kopieren:

- Home Assistant neu starten **oder**
- openWakeWord Add-on neu starten

---

### 5. Bekannte Einschränkungen

- **Sprache:** Colab nutzt Piper TTS – aktuell nur englische Aussprache
- **tflite-Konvertierung:** Gelegentlich Fehler bei ONNX→tflite; bei Problemen [Issue #251](https://github.com/dscripka/openWakeWord/issues/251) prüfen
- **Ressourcen:** Colab Free Tier kann bei hoher Auslastung langsam sein

---

### 6. Referenzen

| Thema              | URL |
|--------------------|-----|
| Colab Training     | https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb |
| HA Wake Words      | https://www.home-assistant.io/voice_control/create_wake_word/ |
| openWakeWord       | https://github.com/dscripka/openWakeWord |
| Scout Setup        | [SCOUT_WAKE_WORD_SETUP.md](SCOUT_WAKE_WORD_SETUP.md) |


---


<a name="fritzbox-adguard-zertifikat"></a>
# FRITZBOX ADGUARD ZERTIFIKAT

## Fritzbox, AdGuard, Zertifikate – Checkliste

**Kontext:** Wenn `fritz.box` nicht erreichbar ist oder Zertifikatsfehler (z. B. HA/Scout unter 192.168.178.54) auftreten, oft: AdGuard/DNS oder geänderte IPs.

---

### 1. Fritzbox-Oberfläche erreichen

- **Standard-IP:** http://192.168.178.1 (Werkseinstellung)
- **Reserve:** http://169.254.1.1
- **Hostname:** fritz.box (funktioniert nur, wenn DNS im LAN die Fritzbox auflöst)

Wenn die Meldung kommt „Sie sind nicht mit Ihrer FRITZ!Box im Heimnetz verbunden“:
- Prüfen: Bin ich im gleichen WLAN/LAN wie die Fritzbox?
- Wenn **AdGuard** (oder anderes DNS-Filter) läuft: Fritzbox und ggf. dein PC als **Clients freigeben** bzw. DNS für fritz.box/192.168.178.1 nicht blockieren/umleiten. Beim ersten AdGuard-Setup mussten dafür oft alle Clients eingetragen werden.

---

### 2. IP-Wechsel prüfen (wegen Zertifikat)

Wenn sich eine **Geräte-IP** geändert hat (z. B. Scout, HA, 4D_RESONATOR (CORE)), passt das Zertifikat oft nicht mehr (ausgestellt für alte IP).

- **In der Fritzbox:**  
  **Heimnetz → Netzwerk → Netzwerkverbindung** (oder **Heimnetz → Netzwerk → Geräte**): Liste der Geräte und zugewiesene IPv4-Adressen. Prüfen, ob z. B. Scout/HA noch 192.168.178.54 haben oder ob die IP gestern/heute gewechselt hat.
- **Statische Zuordnung (DHCP-Reservierung):** Damit sich die IP nicht ändert: In der Fritzbox für das Gerät (z. B. Scout) eine feste IP zuweisen („Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen“).

---

### 3. AdGuard: Clients / DNS für Fritzbox

- **Damit fritz.box und 192.168.178.1 funktionieren:** In AdGuard die Fritzbox (und ggf. deinen Rechner) so einstellen, dass sie nicht blockiert/umgeleitet werden – z. B. „Clients“ bzw. „Geräte“ eintragen und von Filterung ausnehmen oder lokale Auflösung (fritz.box → 192.168.178.1) erlauben.
- **Lokale Domains:** Sicherstellen, dass lokale Namen (fritz.box, ggf. hostname von Scout/HA) von AdGuard korrekt durchgereicht werden (kein Block, keine falsche Weiterleitung).

---

### 4. Zertifikat nach IP-Wechsel (z. B. HA, Scout)

Wenn die **IP** eines Dienstes (HA, Scout) sich geändert hat:
- **Option A:** In der Fritzbox dem Gerät wieder die **alte IP** zuweisen (DHCP-Reservierung auf die bisherige IP).
- **Option B:** Zertifikat/HTTPS des Dienstes (HA, Scout) auf die **neue IP** ausstellen bzw. in HA/Scout so konfigurieren, dass die genutzte URL (IP oder Hostname) zum Zertifikat passt. Dann in CORE (z. B. `.env`: `HASS_URL`, Aufrufe zu HA) die richtige URL nutzen.

---

**Stand:** 2026-03. Bei erneutem Auftreten: zuerst Fritzbox-IP-Liste prüfen, dann AdGuard-Clients/DNS, dann Zertifikat/URL in CORE.


---


<a name="fritzbox-netzwerk-config"></a>
# FRITZBOX NETZWERK CONFIG

## Fritzbox Netzwerk-Konfiguration

**Stand:** 2026-03-02  
**Ausgelesen via:** `src/scripts/_fetch_fritzbox_info.py` (TR-064 API)

---

### Hardware

| Parameter | Wert |
|-----------|------|
| Modell | FRITZ!Box 7583 |
| Firmware | 8.20 |
| IP (LAN) | 192.168.178.1 |
| MAC | 74:42:7F:CC:70:62 |
| Hostname | MaFritzBox |

---

### WAN-Verbindung

| Parameter | Wert |
|-----------|------|
| Status | Online |
| Externe IPv4 | 87.79.192.110 |
| Externe IPv6 | 2001:4dd0:af17:822b:7642:7fff:fecc:705f |

---

### DHCP-Konfiguration

| Parameter | Wert |
|-----------|------|
| DHCP Server | Aktiviert |
| DHCP Range | 192.168.178.2 – 192.168.178.200 |
| Subnetzmaske | 255.255.255.0 |
| Standard-Gateway | 192.168.178.1 |
| DNS Server (für Clients) | **192.168.178.54** (Home Assistant / AdGuard) |
| Domain | MaFritzBox |
| DHCP Relay | Deaktiviert |

**Wichtig:** Die Fritzbox verteilt `192.168.178.54` als DNS – das ist Home Assistant mit AdGuard. Damit läuft der gesamte DNS-Traffic über AdGuard.

---

### Kritische Geräte (aktiv, mit fester IP)

| Name | IP | MAC | Funktion |
|------|----|----|----------|
| HOME | 192.168.178.54 | 2C:CF:67:68:45:32 | **Home Assistant / AdGuard DNS** |
| MtH11 | 192.168.178.20 | 18:C0:4D:DB:2D:B0 | Haupt-PC (4D_RESONATOR (CORE)) |
| HACS-PI4 | 192.168.178.154 | E4:5F:01:8C:22:46 | Raspberry Pi 4 |
| DCS-6100LH | 192.168.178.100 | B0:C5:54:5D:B3:61 | D-Link Kamera |
| samsungq95 | 192.168.178.123 | C0:23:8D:EB:07:1D | Samsung TV (LAN) |
| Mini-Regal | 192.168.178.108 | F0:EF:86:0D:A9:0E | Google Mini |
| Google-Nest-Mini | 192.168.178.23 | 20:1F:3B:78:08:64 | Google Mini (Flur) |
| MiniSTisch | 192.168.178.28 | E4:F0:42:1F:DB:EB | Google Mini (Schreibtisch) |
| minis1 | 192.168.178.4 | 14:C1:4E:94:CB:77 | Google Mini |
| Center | 192.168.178.80 | DC:E5:5B:6A:85:B2 | Sonos/Center |
| VMSucker | 192.168.178.91 | 78:11:DC:5F:F7:4D | Staubsauger |
| p1s3d | 192.168.178.95 | 24:58:7C:DF:3B:A0 | 3D-Drucker |

---

### ESP/Smart-Home Geräte (aktiv)

| Name | IP | MAC |
|------|----|----|
| ledcontrollernew | 192.168.178.15 | B4:E8:42:28:7C:3A |
| ledkueche | 192.168.178.17 | B4:E8:42:DF:42:66 |
| Flur | 192.168.178.22 | 10:D5:61:1A:21:D7 |
| ESP-EAEACC | 192.168.178.26 | DC:4F:22:EA:EA:CC |
| ESP-Bettlicht | 192.168.178.27 | 24:A1:60:19:71:98 |
| ESP-PIR-Keller | 192.168.178.29 | 80:7D:3A:48:2B:06 |
| ESP-Deckenlampe | 192.168.178.30 | 10:D5:61:2C:0D:79 |
| Schreibtischlicht | 192.168.178.33 | 98:17:3C:3B:F2:C4 |
| protuer | 192.168.178.34 | 60:74:F4:87:61:D8 |
| ProTisch | 192.168.178.35 | D4:AD:FC:AC:68:EA |
| proregal | 192.168.178.36 | 60:74:F4:84:1C:04 |
| Andon1 | 192.168.178.37 | D0:C9:07:6D:37:B2 |
| Andon2 | 192.168.178.38 | D0:C9:07:70:97:C6 |
| Temp-Bridge | 192.168.178.39 | D8:1F:12:F6:29:AA |
| espbad | 192.168.178.42 | 70:89:76:92:2B:D2 |
| C52A | 192.168.178.43 | BC:07:1D:B9:5F:22 |
| Mehrfachsteckdose | 192.168.178.87 | 50:8B:B9:AE:61:63 |

---

### Netzwerk-Infrastruktur

| Name | IP | MAC | Typ |
|------|----|----|-----|
| powerlinemain | - | 34:31:C4:D0:18:1E | Powerline-Adapter |
| fritz.powerline | 192.168.178.31 | 42:49:79:F1:76:CF | Fritz Powerline |
| wlan0 | 192.168.178.21 | A0:92:08:FF:22:EF | WLAN-Gerät |
| wlan0 | 192.168.178.117 | 70:89:76:93:5E:0E | WLAN-Gerät |
| pc-proregal | 192.168.178.32 | 60:74:F4:24:4C:EC | PC/Regal |

---

### Bekannte Einschränkungen

1. **IPv6 DNS:** Die Fritzbox 7583 gibt per DHCPv6 trotzdem sich selbst als DNS aus. Google Minis bevorzugen IPv6 und umgehen damit AdGuard. Siehe `ADGUARD_HOME_SETUP.md`.

2. **Hairpin-NAT:** Nicht aktiviert (Standard). Externe URLs (z.B. `mth-home2go.duckdns.org`) funktionieren intern nur, wenn AdGuard/DNS die Domain auf die lokale IP umschreibt.

3. **TR-064 Limitierung:** Erweiterte Einstellungen (Portfreigaben, MyFRITZ, etc.) sind über TR-064 nicht vollständig abrufbar.

---

### Zugriff

- **Web-UI:** http://192.168.178.1 oder http://fritz.box
- **API-User:** `HA_AC` (in `.env` als `FRITZBOX_USERNAME`)
- **Skript:** `src/scripts/_fetch_fritzbox_info.py`

---

### Referenzen

- `docs/03_INFRASTRUCTURE/ADGUARD_HOME_SETUP.md` – AdGuard DNS-Konfiguration
- `docs/03_INFRASTRUCTURE/FRITZBOX_ADGUARD_ZERTIFIKAT.md` – Troubleshooting bei Zertifikat-/IP-Problemen


---


<a name="ha-scout-mx-integration"></a>
# HA SCOUT MX INTEGRATION

## HA Configuration for Scout MX Brio (via go2rtc)
## Add this to your HA configuration.yaml

camera:
  - platform: generic
    name: "Scout MX"
    still_image_url: "http://<SCOUT_IP>:1984/api/frame.jpeg?src=mx_brio"
    stream_source: "rtsp://<SCOUT_IP>:8554/mx_brio"
    verify_ssl: false

## Alternative (Passive/Raw FFmpeg - less efficient):
## camera:
##   - platform: ffmpeg
##     input: /dev/video0
##     name: "Scout MX Raw"


---


<a name="mtls-migration-plan"></a>
# MTLS MIGRATION PLAN

## mTLS-Migrationsplan – GQA Refactor F3 (unified-auth-mtls)

**Zweck:** Einheitliches mTLS-Schema für alle Service-to-Service-Kommunikation in CORE. Ersetzt den Wildcard-Token-Ansatz durch Zertifikats-basierte gegenseitige Authentifizierung.

**Stand:** 2026-03  
**Status:** Konzept / Planung  
**Geschützte Module:** Auth/Credentials (Stufe 1) – Umsetzung nur nach Freigabe durch Code-Sicherheitsrat.

---

### 1. Aktuelle Auth-Struktur (Ist-Zustand)

#### 1.1 `src/api/auth_webhook.py`

| Funktion | Methode | Env-Variable | Verwendung |
|----------|---------|---------------|------------|
| `verify_whatsapp_auth` | Shared-Secret Header | `CORE_WEBHOOK_SECRET` | X-CORE-WEBHOOK-SECRET |
| `verify_ha_auth` | Bearer Token | `HA_WEBHOOK_TOKEN` | Bearer für /webhook/ha_action, /webhook/inject_text |
| `verify_oc_auth` | API-Key / Bearer | `OPENCLAW_GATEWAY_TOKEN` | X-API-Key oder Bearer für /api/oc/* |

**Positiv:** Constant-time Vergleich (`secrets.compare_digest`), keine Secrets im Code.  
**Risiko:** Token in .env; Rotation manuell; kein Identitätsnachweis (jeder mit Token = gleichberechtigt).

#### 1.2 Weitere Token-Verbindungen

| Verbindung | Protokoll | Auth | Env |
|------------|-----------|------|-----|
| CORE → OpenClaw Gateway | HTTP/HTTPS | Bearer | OPENCLAW_GATEWAY_TOKEN |
| Scout/HA → OpenClaw | HTTP POST | Bearer | OPENCLAW_GATEWAY_TOKEN |
| Scout → 4D_RESONATOR (CORE) (SSH) | SSH | Passwort/Key | HA_SSH_USER, HA_SSH_PASSWORD, SSH_KEY_PATH |
| Cursor → VPS (MCP) | HTTP/SSH | (nicht dokumentiert) | MCP-Server auf VPS:8001 |
| 4D_RESONATOR (CORE) → ChromaDB (VPS) | HTTP | Keine | CHROMA_HOST, CHROMA_PORT |
| VPS SSH | SSH | Passwort/Key | VPS_USER, VPS_PASSWORD, VPS_SSH_KEY |

---

### 2. mTLS-Schema (Soll-Zustand)

#### 2.1 Zertifikats-Hierarchie

```
                    ┌─────────────────────────────────────┐
                    │  CORE Root CA (self-signed)         │
                    │  CN=core-ca.local, 10 Jahre        │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Server CA      │       │  Client CA      │       │  (Reserve)       │
│  CN=core-srv   │       │  CN=core-cli   │       │                  │
└────────┬────────┘       └────────┬────────┘       └─────────────────┘
         │                         │
    ┌────┴────┐              ┌─────┴─────┐
    │         │              │           │
    ▼         ▼              ▼           ▼
┌───────┐ ┌───────┐    ┌─────────┐ ┌─────────┐
│CORE  │ │ MCP   │    │ cursor  │ │ oc-brain│
│ API   │ │ Server│    │ client  │ │ client  │
│(Dread)│ │(VPS)  │    │         │ │         │
└───────┘ └───────┘    └─────────┘ └─────────┘
    │         │              │           │
    │         │         ┌────┴────┐      │
    │         │         │         │      │
    ▼         ▼         ▼         ▼      ▼
┌─────────┐ ┌─────────┐
│ scout   │ │ ha      │
│ client  │ │ client  │
└─────────┘ └─────────┘
```

**Prinzip:**  
- **Root CA:** Eine zentrale CA pro CORE-Installation (oder pro Mandant).  
- **Server CA:** Signiert Server-Zertifikate (CORE API, MCP Server, OpenClaw Gateway).  
- **Client CA:** Signiert Client-Zertifikate (Cursor, Scout, OMEGA_ATTRACTOR, HA).  
- **Trennung:** Server- und Client-CA getrennt → Revocation pro Rolle möglich.

#### 2.2 Zertifikats-Mapping pro Verbindung

| Verbindung | Server-Cert | Client-Cert | Port |
|------------|-------------|-------------|------|
| **Cursor → VPS (MCP)** | MCP-Server (VPS) | cursor-client | 8001 (TLS) |
| **Scout → 4D_RESONATOR (CORE)** | CORE API | scout-client | 8000 (TLS) |
| **OMEGA_ATTRACTOR → CORE API** | CORE API | oc-brain-client | 8000 (TLS) |
| **HA → CORE API** | CORE API | ha-client | 8000 (TLS) |
| **CORE → OpenClaw** | OpenClaw Gateway | core-client | 18789/443 (TLS) |
| **CORE → ChromaDB** | ChromaDB (optional) | core-client | 8000 (TLS) |

**Hinweis:** ChromaDB unterstützt mTLS nicht nativ; Option: Reverse-Proxy (z. B. Nginx) mit mTLS vor ChromaDB.

#### 2.3 Subject-Namen (SAN/CN)

| Zertifikat | CN | SAN (Subject Alternative Names) |
|-------------|-----|----------------------------------|
| core-api-server | core-api.dreadnought.local | DNS:core-api.local, IP:192.168.178.x |
| mcp-server | mcp.vps.core.local | DNS:mcp.vps.core.local, IP:VPS_IP |
| openclaw-server | openclaw.vps.core.local | DNS:openclaw.vps.core.local |
| cursor-client | cursor.dreadnought.local | - |
| scout-client | scout.raspi.local | - |
| oc-brain-client | oc-brain.vps.core.local | - |
| ha-client | ha.scout.local | - |
| core-client | core.dreadnought.local | - |

---

### 3. Migrations-Schritte (Token → mTLS)

#### Phase 1: Vorbereitung (ohne Produktionsänderung)

1. **CA und Zertifikate generieren**  
   - Skript: `src/scripts/generate_mtls_certs.py` (siehe Abschnitt 6)  
   - Ausgabe: `data/certs/` (nicht versionieren, .gitignore)

2. **Zertifikats-Pfade in .env dokumentieren**  
   - Neue Variablen: `MTLS_CA_CERT`, `MTLS_SERVER_CERT`, `MTLS_SERVER_KEY`, `MTLS_CLIENT_CERT`, `MTLS_CLIENT_KEY`  
   - Noch nicht aktiv nutzen

3. **Fallback-Logik in auth_webhook.py vorbereiten**  
   - Neue Funktion `verify_mtls_or_token()`: Zuerst mTLS prüfen, bei fehlendem Client-Cert → Token-Fallback

#### Phase 2: Dual-Mode (mTLS + Token parallel)

4. **CORE API:** TLS aktivieren (uvicorn mit ssl_context), mTLS optional  
   - Client-Cert-Validierung: Nur wenn Request Client-Cert mitschickt  
   - Token weiterhin akzeptiert für Legacy-Clients

5. **OpenClaw Gateway:** mTLS als zusätzliche Auth-Option (wenn OpenClaw das unterstützt; sonst Nginx vor Gateway)

6. **MCP-Server:** TLS + optional mTLS (Cursor-Client-Cert)

#### Phase 3: Migration pro Client

7. **Scout/HA:** Client-Cert auf Raspi deployen, HA Automation auf HTTPS+mTLS umstellen  
8. **OMEGA_ATTRACTOR:** Client-Cert in OpenClaw-Container, Requests mit Cert  
9. **Cursor:** MCP-Client mit Client-Cert konfigurieren  
10. **CORE → OpenClaw:** openclaw_client.py auf mTLS umstellen

#### Phase 4: Token-Deprecation

11. **Token-Fallback deaktivieren** (konfigurierbar: `MTLS_LEGACY_TOKEN_FALLBACK=0`)  
12. **Alte Token aus .env entfernen** (nach Bestätigung aller Clients migriert)  
13. **rotate_tokens.py** anpassen oder obsolet

---

### 4. Fallback für Legacy-Clients

#### 4.1 Konfiguration

```env
## .env
MTLS_LEGACY_TOKEN_FALLBACK=1   # 1 = Token weiterhin akzeptieren, 0 = nur mTLS
MTLS_REQUIRE_CLIENT_CERT=0     # 0 = optional (Fallback möglich), 1 = Pflicht
```

#### 4.2 Auth-Flow (auth_webhook.py – konzeptionell)

```python
## Pseudocode – nicht direkt übernehmen
def verify_oc_auth_mtls_or_token(request):
    # 1. mTLS: Client-Cert vorhanden und von Client-CA signiert?
    if request.scope.get("transport") and has_valid_client_cert(request):
        return  # OK
    # 2. Fallback: Token (wie bisher)
    if MTLS_LEGACY_TOKEN_FALLBACK:
        verify_oc_auth(request)  # X-API-Key / Bearer
    else:
        raise HTTPException(401, "mTLS erforderlich")
```

#### 4.3 Welche Clients sind „Legacy“?

| Client | Migrations-Priorität | Begründung |
|--------|----------------------|------------|
| WhatsApp Webhook | Niedrig | Externer Dienst (Meta), kein Client-Cert möglich → Token bleibt |
| HA/Scout | Mittel | Raspi kann Cert hosten; HA-Automation anpassbar |
| OMEGA_ATTRACTOR | Hoch | VPS-Container, Cert-Deploy machbar |
| Cursor | Hoch | Lokaler Client, Cert auf 4D_RESONATOR (CORE)/PC |
| ChromaDB-Zugriff | Optional | Proxy mit mTLS oder SSH-Tunnel |

**Ausnahme:** WhatsApp-Webhook (`CORE_WEBHOOK_SECRET`) bleibt dauerhaft Token-basiert – Meta sendet kein Client-Cert.

---

### 5. Sicherheits-Constraints (Audit-Checkliste)

- [ ] **Keine Secrets im Code** – Zertifikate nur über Pfade aus .env
- [ ] **Principle of Least Privilege** – Jeder Client-Cert nur für die nötigen Dienste
- [ ] **Gestaffelte Schutzlinien** – CA-Key offline/gesichert; Server/Client-Certs mit kurzer Laufzeit (z. B. 1 Jahr)
- [ ] **Revocation** – CRL oder OCSP vorbereiten (späte Phase)
- [ ] **Constant-time** – Zertifikatsvergleich keine Short-Circuit-Vergleiche

---

### 6. Cert-Generation-Script

Skript: `src/scripts/generate_mtls_certs.py`

```bash
python -m src.scripts.generate_mtls_certs [--output data/certs] [--days 365]
```

Erzeugt CA, Server- und Client-Zertifikate für Entwicklung und erste Tests.  
**Produktion:** CA-Key separat, ideal mit HSM oder Vault.

#### 6.1 Ausgabe-Struktur

| Datei | Verwendung |
|-------|------------|
| `ca_root.pem`, `ca_root.key` | Root CA (geheim halten) |
| `ca_srv.pem`, `ca_cli.pem` | Intermediate CAs |
| `core-api.pem/.key` | CORE API Server |
| `mcp-server.pem/.key` | MCP-Server (VPS) |
| `openclaw-server.pem/.key` | OpenClaw Gateway |
| `cursor.pem/.key`, `scout.pem/.key`, etc. | Client-Zertifikate |
| `chain_server.pem` | CA-Chain für Server-Validierung |
| `chain_client.pem` | CA-Chain für Client-Validierung |

---

### 7. Referenzen

- `src/api/auth_webhook.py` – aktuelle Token-Auth
- `docs/02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md`
- `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md`
- `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` – Freigabe-Prozess


---


<a name="mx-kamera-core-hoeren-sehen"></a>
# MX KAMERA CORE HOEREN SEHEN

## MX-Kamera (Logitech Brio) – CORE hören und sehen

Kurzanleitung: So nutzt CORE die MX/Brio am 4D_RESONATOR (CORE)-PC zum **Sehen** und (optional) zum **Hören**.  
**Scout-MX:** USB-MX am Scout (Raspi/HA) → Proof „Sehen“ mit Quelle `scout_mx` (siehe Abschnitt „Scout-MX einbinden“).

---

### Scout-MX einbinden (Kamera am Scout/Raspi/HA)

**Stand:** `SCOUT_MX_SNAPSHOT_URL` zeigt auf `camera.scout_mx`. Sobald diese Kamera in HA existiert, läuft der Proof „Sehen“ mit Quelle scout_mx.

Damit Proof „Sehen“ mit Quelle **scout_mx** funktioniert:

1. **HA-Seite:** USB-MX am Scout in Home Assistant sichtbar machen.
   - **Typisch:** Generic Camera oder **FFmpeg**-Integration mit Eingabe `/dev/video0` (HA OS erkennt UVC-Kamera).
   - **Entity-ID:** z.B. `camera.scout_mx` (frei wählbar; Default in CORE: `camera.scout_mx`).
   - **Anlegen:** YAML (`configuration.yaml`) oder **Einstellungen → Geräte & Dienste → Kamera hinzufügen** (FFmpeg/Generic Camera).
2. **CORE-Seite:** `SCOUT_MX_SNAPSHOT_URL` setzen = `HASS_URL` + `/api/camera_proxy/<entity_id>`.
   - **Empfohlen:** `python -m src.scripts.setup_scout_mx` (oder `set_scout_mx_snapshot_url`) ausführen. Liest HASS_URL (Fallback HA_URL) und HASS_TOKEN (Fallback HA_TOKEN) aus .env; baut die URL; prüft optional per GET gegen HA, ob die Camera-Entity existiert; schreibt nur die Zeile `SCOUT_MX_SNAPSHOT_URL=…` in .env (bestehende Zeile wird ersetzt, sonst angehängt; keine Löschung anderer .env-Inhalte).
   - **Aufruf:** `python -m src.scripts.setup_scout_mx [--entity camera.scout_mx] [--no-check] [--dry-run]`. Entity-ID auch per Umgebungsvariable `SCOUT_MX_ENTITY_ID`. Mit `--dry-run` wird nur die Zeile ausgegeben (zum manuellen Eintrag).
   - **Manuell:** In `.env` eintragen: `SCOUT_MX_SNAPSHOT_URL=https://<Scout-IP>:8123/api/camera_proxy/camera.scout_mx` (HASS_TOKEN für Proxy-Aufruf setzen).
3. **Proof ausführen:** `python -m src.scripts.proof_hoert_sieht_spricht` → Abschnitt „Sehen“ nutzt Scout-MX, wenn konfiguriert.

Siehe auch: `SCOUT_USB_KAMERA_MIKRO_HA_OS.md`, `.env.template` (SCOUT_MX_SNAPSHOT_URL, HASS_URL, HASS_TOKEN).

---

### Sehen (MX als Bildquelle)

**Reihenfolge der Snapshot-Quellen** (in `go2rtc_client.get_snapshot`):

1. **go2rtc** (localhost:1984, Stream `pc`) – falls go2rtc mit Brio-Stream läuft
2. **MX lokal** – `CAMERA_SNAPSHOT_URL_MX` (Standard: `http://localhost:8555/snapshot.jpg`)
3. **HA/Remote** – `CAMERA_SNAPSHOT_URL` (z.B. `camera.balkon`)

#### Option A: On-Demand-Snapshot (Brio nur bei Abruf)

1. In einem Terminal starten:
   ```bash
   python -m src.scripts.camera_snapshot_server
   ```
2. Server läuft auf Port 8555. `go2rtc_client` nutzt automatisch `http://localhost:8555/snapshot.jpg` (Default für `CAMERA_SNAPSHOT_URL_MX`).
3. Kein Eintrag in `.env` nötig, falls Default passt. Sonst:
   ```env
   CAMERA_SNAPSHOT_URL_MX=http://localhost:8555/snapshot.jpg
   ```
4. Gerätename: Wenn die Brio unter Windows als **„Logi Capture“** erscheint, bleibt `CAMERA_DEVICE_NAME` leer oder auf `Logitech BRIO` – der Snapshot-Server versucht nacheinander „Logitech BRIO“, „Logi Capture“, „Logitech BRIO“.

**Tests:**

- `python -m src.scripts.mx_save_images_only` → Bilder in `data/mx_test/`
- `python -m src.scripts.proof_hoert_sieht_spricht` → Abschnitt „Sehen“ nutzt dieselbe Quelle

#### Option B: go2rtc mit Brio-Dauerstream

1. `driver/go2rtc_win64/go2rtc.yaml` wie in `go2rtc_brio_example.yaml` (Brio als Stream `pc`) konfigurieren
2. go2rtc starten (z.B. `go2rtc.exe` im Ordner)
3. `CAMERA_SNAPSHOT_URL_MX` leer lassen oder weglassen – dann wird zuerst go2rtc (localhost:1984) verwendet

---

### Hören (Mikrofon am PC)

- **sounddevice** nutzt das Standard-Mikrofon (z.B. Razer Seiren V3 Mini oder „Mikrofon (Logitech BRIO)“).
- Skript: `python -m src.scripts.dreadnought_listen` – Aufnahme → WAV → Event an OMEGA_ATTRACTOR.
- Unter Windows das gewünschte Mikrofon als **Standard-Eingabegerät** setzen, dann braucht CORE keine weitere Konfiguration.

---

### Kurz-Checkliste

| Schritt | Befehl / Aktion |
|--------|------------------|
| MX-Snapshot-Server starten | `python -m src.scripts.camera_snapshot_server` |
| MX-Bilder speichern | `python -m src.scripts.mx_save_images_only` |
| Proof (Sehen + Sprechen + Hören) | `python -m src.scripts.proof_hoert_sieht_spricht` |
| Hören (Aufnahme → Event) | `python -m src.scripts.dreadnought_listen` |
| Scout-MX-URL in .env setzen | `python -m src.scripts.setup_scout_mx` oder `set_scout_mx_snapshot_url` (Optionen: `--entity camera.scout_mx`, `--no-check`, `--dry-run`) |

Siehe auch: `CAMERA_GO2RTC_WINDOWS.md`, `CORE_HOERT_SIEHT_SPRICHT_STATUS.md`, `SCOUT_USB_KAMERA_MIKRO_HA_OS.md`.


---


<a name="oc-brain-leere-nachrichten-diagnose"></a>
# OC BRAIN LEERE NACHRICHTEN DIAGNOSE

## OMEGA_ATTRACTOR: "I didn't receive any text" – Diagnose

**Symptom (Screenshot 2026-03-03):** User schickt Nachricht im Gateway-Chat; OMEGA_ATTRACTOR antwortet: "I didn't receive any text in your message. Please resend or add a caption." Eine User-Blase wirkt leer/korrupt, eine zweite enthält "das oder?".

**Ursache (Vermutung):** Leere oder nicht korrekt übermittelte Nutzer-Eingabe beim Gateway (Frontend → Backend). Mögliche Auslöser: zu schnelles Absenden, Encoding, oder UI-Bug beim Senden.

**Minimal-invasive Maßnahmen (ohne OMEGA_ATTRACTOR zu gefährden):**

1. **Update ausführen:** Im Dashboard steht "Update available: v2026.3.2 (running v2026.2.27)". Update durchführen – kann den Parsing-/Payload-Bug beheben.
2. **Leere Eingabe vermeiden:** Vor dem Absenden prüfen, dass Text im Feld steht; nicht mit leerem Input senden.
3. **Bei erneutem Auftreten:** Browser-Konsole (F12) prüfen, ob beim Senden Fehler erscheinen oder der Request-Body leer ist. Falls ja: OpenClaw-Issue oder -Release-Notes prüfen.

**Kein Zugriff auf Gateway-Frontend-Code im Repo** – Fix liegt beim OpenClaw-Product. Wir ändern hier nichts am laufenden OMEGA_ATTRACTOR-Backend.


---


<a name="openwakeword-models"></a>
# OPENWAKEWORD MODELS

## openWakeWord – Verfügbare Modelle

**Zweck:** Übersicht der vordefinierten und Custom Wake Word Modelle für CORE/Scout.

**Quelle:** [openWakeWord GitHub](https://github.com/dscripka/openWakeWord), [Hugging Face](https://huggingface.co/davidscripka/openwakeword)

---

### 1. Vordefinierte Modelle (openWakeWord v0.5.1 / v0.6.0)

| Modell-ID      | Wake Word      | Beschreibung                    | Ähnlich zu |
|----------------|----------------|----------------------------------|------------|
| `alexa`        | alexa          | Ein-Wort-Trigger                 | –          |
| `hey_mycroft`  | hey mycroft    | Zwei-Wort-Phrase                | hey core  |
| `hey_jarvis`   | hey jarvis     | Zwei-Wort-Phrase (Computer-Assistent) | computer, hey core |
| `hey_rhasspy`  | hey rhasspy    | Zwei-Wort-Phrase                | hey core  |
| `timer`        | timer-Befehle  | Speziell für Timer-Phrasen      | –          |
| `weather`      | weather-Befehle| Speziell für Wetter-Phrasen     | –          |

**Download-URLs (GitHub Releases v0.5.1):**
- `https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/alexa_v0.1.tflite`
- `https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/hey_mycroft_v0.1.tflite`
- `https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/hey_jarvis_v0.1.tflite`
- `https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/hey_rhasspy_v0.1.tflite`
- `https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/timer_v0.1.tflite`
- `https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/weather_v0.1.tflite`

---

### 2. „Computer“ und „Core“

#### 2.1 „Computer“

| Frage                         | Antwort |
|------------------------------|---------|
| Gibt es „computer“ vordefiniert? | **Nein** |
| Ähnliche Modelle              | `hey_jarvis` (Computer-Assistent-Kontext) |
| Lösung                        | Custom Training (siehe [Custom Wake Word Training](#3-custom-wake-word-training)) |

#### 2.2 „Core“ / „hey core“

| Frage                         | Antwort |
|------------------------------|---------|
| Gibt es „core“ vordefiniert? | **Nein** |
| Ähnliche Modelle              | `hey_mycroft`, `hey_jarvis`, `hey_rhasspy` (alle Zwei-Wort-Phrasen) |
| Lösung                        | Custom Training (siehe [Custom Wake Word Training](#3-custom-wake-word-training)) |

---

### 3. Home Assistant Add-on: „ok nabu“

Das **ok nabu** Wake Word wird von Home Assistant empfohlen und ist im openWakeWord Add-on bzw. der Wyoming-Integration verfügbar. Es stammt aus dem HA Voice-Projekt und ist **nicht** Teil der offiziellen openWakeWord-Modellliste – wird aber vom HA Add-on bereitgestellt.

**Verwendung:** Zum Testen der Wake-Word-Pipeline vor dem Training eigener Modelle.

---

### 4. Lizenz

Alle vordefinierten Modelle: **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International** (CC BY-NC-SA 4.0) – wegen Datensätzen mit restriktiver Lizenz im Training.

---

### 5. Referenzen

| Thema              | URL |
|--------------------|-----|
| openWakeWord       | https://github.com/dscripka/openWakeWord |
| Hugging Face       | https://huggingface.co/davidscripka/openwakeword |
| Wyoming-openWakeWord | https://github.com/rhasspy/wyoming-openwakeword |
| HA Wake Words      | https://www.home-assistant.io/voice_control/create_wake_word/ |


---


<a name="scout-assist-pipeline"></a>
# SCOUT ASSIST PIPELINE

## Scout Assist-Pipeline: Sprachbefehle an CORE

**Zweck:** Sprachbefehle vom Scout-Mikrofon über die HA Assist-Pipeline an CORE weiterleiten. CORE führt Triage durch (HA-Aktion oder OMEGA_ATTRACTOR), die Antwort wird per TTS auf dem Mini-Speaker ausgegeben.

---

### 1. Architektur

```
User spricht
    ↓
Scout Mikrofon (USB oder integriert)
    ↓
openWakeWord ("hey core" / "core") → Pipeline startet
    ↓
Whisper STT → transkribierter Text
    ↓
CORE API (4D_RESONATOR (CORE)) POST /webhook/assist
    ↓
Triage (SLM): command | deep_reasoning | chat
    ↓
├─ command → HA-Aktion (Licht, etc.) via HAClient
└─ deep_reasoning/chat → OMEGA_ATTRACTOR oder lokales Gemini
    ↓
Antwort-Text
    ↓
Piper TTS → Mini-Speaker (media_player.schreibtisch o.ä.)
```

**Netzwerk:**
- **Scout (HA):** 192.168.178.54 (Raspi 5)
- **4D_RESONATOR (CORE) (CORE API):** 192.168.178.20, Port 8000
- Scout muss 4D_RESONATOR (CORE) per HTTP erreichen können: `http://192.168.178.20:8000`

---

### 2. CORE-Verbindung zu HA

CORE verbindet sich **zu** HA (nicht umgekehrt):

- **Client:** `src/connectors/home_assistant.py` (HomeAssistantClient)
- **Variablen:** `HASS_URL` / `HA_URL`, `HASS_TOKEN` / `HA_TOKEN`
- **Funktionen:** `call_service()`, `get_states()`, etc.
- **Richtung:** 4D_RESONATOR (CORE) → Scout (HTTPS zu 192.168.178.54:8123)

Die **Assist-Pipeline** benötigt die **umgekehrte** Richtung: HA (Scout) → CORE (4D_RESONATOR (CORE)). Dafür nutzt HA einen `rest_command`, der an die CORE API sendet.

---

### 3. Benötigte HA-Variablen (.env auf 4D_RESONATOR (CORE))

| Variable | Beschreibung | Beispiel |
|---------|--------------|----------|
| `HASS_URL` / `HA_URL` | HA-URL (Scout) | `https://192.168.178.54:8123` |
| `HASS_TOKEN` / `HA_TOKEN` | Long-Lived Token für HA | (aus HA Profil) |
| `HA_WEBHOOK_TOKEN` | Bearer-Token für `/webhook/assist`, `/webhook/inject_text` | Zufälliger String (z.B. `openssl rand -hex 24`) |

**Wichtig:** `HA_WEBHOOK_TOKEN` muss in `.env` gesetzt sein, sonst lehnt die CORE API Anfragen ab (503).

---

### 4. HA Add-ons (Scout)

| Add-on | Zweck |
|--------|-------|
| **Assist Microphone** | **Audio-Input** – liest vom USB-Mikro (Brio/Headset), streamt an Wyoming. **Ohne dieses Add-on erreicht kein Audio die Pipeline.** |
| **Whisper** | Speech-to-Text (offenes Modell, beliebige Sprache) |
| **openWakeWord** | Wake-Word-Erkennung ("hey core", "core", "computer") |
| **Piper** | Text-to-Speech (lokal, schnell) |

Installation: Einstellungen → Add-ons → Add-on-Store. Nach Installation erscheinen die Dienste unter Wyoming-Integration.

**Hinweis:** go2rtc liefert Video+Audio für RTSP/Streaming, aber **nicht** an die Assist-Pipeline. Die Pipeline braucht das Assist Microphone Add-on für Spracheingabe.

---

### 5. Wake-Word Konfiguration

- **openWakeWord** unterstützt vordefinierte und eigene Wake-Wörter.
- Für "hey core" oder "core": In der openWakeWord-Konfiguration das passende Modell wählen oder ein Custom-Modell trainieren.
- Dokumentation: [HA Wake Words](https://www.home-assistant.io/voice_control/create_wake_word/)

---

### 6. rest_command: Text an CORE senden

In `configuration.yaml` oder als YAML-Konfiguration:

```yaml
## Geheimnisse (Einstellungen → Geheimnisse oder secrets.yaml):
##   core_api_url: "http://192.168.178.20:8000"
##   core_webhook_token: "<HA_WEBHOOK_TOKEN aus .env>"

rest_command:
  core_assist:
    url: "{{ core_api_url }}/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer {{ core_webhook_token }}"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

**Ohne Geheimnisse (direkt, nicht empfohlen für Produktion):**

```yaml
rest_command:
  core_assist:
    url: "http://192.168.178.20:8000/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer DEIN_HA_WEBHOOK_TOKEN"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

---

### 7. CORE Conversation Agent (empfohlen)

**Custom Integration** `core_conversation` – empfängt Text von der Assist-Pipeline, sendet an CORE `/webhook/inject_text`, gibt Antwort für TTS zurück.

#### 7.0 Installation der CORE Conversation Integration

1. Ordner `ha_integrations/core_conversation` nach `config/custom_components/core_conversation/` kopieren.
2. HA neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → "CORE Conversation".
4. **CORE API URL:** z.B. `http://192.168.178.20:8000`
5. **Bearer Token:** `HA_WEBHOOK_TOKEN` aus `.env`

Vollständige Anleitung: `ha_integrations/core_conversation/README.md`

#### 7.1 Workaround: input_text + Automation (falls Integration nicht nutzbar)

Wenn der Text auf anderem Weg in `input_text.assist_command` landet (z.B. von einem externen Skript oder einer anderen Integration):

```yaml
input_text:
  assist_command:
    name: "Assist-Befehl für CORE"
    max: 500

automation:
  - alias: "Assist-Text an CORE senden"
    trigger:
      - platform: state
        entity_id:
          - input_text.assist_command
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | length > 0 }}"
    action:
      - service: rest_command.core_assist
        data:
          text: "{{ states('input_text.assist_command') }}"
      - service: input_text.set_value
        target:
          entity_id: input_text.assist_command
        data:
          value: ""
```

**Hinweis:** Damit die volle Voice-Pipeline funktioniert, muss der transkribierte Text aus der Assist-Pipeline in `input_text.assist_command` geschrieben werden. Dafür ist ein **Custom Conversation Agent** nötig – die CORE Conversation Integration (Abschnitt 7.0) löst das vollständig.

**Event-basierte Alternative:** `assist_pipeline.run_stage` feuert `stt-end` (mit `stt_output.text`) und `intent-start`. Eine Automation könnte auf `stt-end` triggern und CORE aufrufen – aber die Antwort kann nicht zurück in die Pipeline injiziert werden (TTS würde fehlen). Daher: Custom Agent erforderlich.

#### 7.2 CORE API Antwort und TTS

Mit **CORE Conversation Integration**: Der Agent ruft `/webhook/inject_text` auf. CORE gibt `{"status":"ok","reply":"<Antworttext>"}` zurück. **HA Piper** spricht die Antwort über den konfigurierten Media Player (TTS in der Assist-Pipeline).

Ohne Custom Agent (rest_command-Workaround): `/webhook/assist` würde CORE-seitig TTS auslösen – für die volle Voice-Pipeline ist die Integration vorzuziehen.

---

### 8. Assist-Pipeline einrichten

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen**
2. **Name:** z.B. "CORE"
3. **Sprache:** Deutsch (oder gewünschte Sprache)
4. **Conversation Agent:** **CORE Conversation** (nach Installation der Custom Integration, siehe Abschnitt 7.0)
5. **Speech-to-Text:** Whisper
6. **Text-to-Speech:** Piper
7. **Wake Word:** openWakeWord (falls verfügbar)

Ohne CORE Conversation Agent arbeitet die Pipeline mit dem Standard-HA-Agent. Für CORE-Anbindung die Integration aus Abschnitt 7.0 installieren.

---

### 9. Netzwerk-Checkliste

| Von | Nach | Port | Protokoll |
|-----|------|------|-----------|
| Scout (HA) | 4D_RESONATOR (CORE) | 8000 | HTTP |
| 4D_RESONATOR (CORE) | Scout (HA) | 8123 | HTTPS |
| Scout | Wyoming (Whisper, Piper, openWakeWord) | Add-on-intern | - |

**Test von Scout aus:**
```bash
## Auf dem Scout (SSH) oder von einem Gerät im gleichen Netz:
curl -X POST http://192.168.178.20:8000/webhook/assist \
  -H "Authorization: Bearer DEIN_HA_WEBHOOK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

---

### 10. Wyoming-Integration verifizieren

**Test-Script:** `python -m src.scripts.test_ha_voice_integration`

Prüft ob Whisper STT, Piper TTS und openWakeWord in HA verfügbar sind. Nutzt `HomeAssistantClient` aus `src/connectors/home_assistant.py`; bei SSL-Problemen (Self-Signed/IP-Zertifikat) Fallback mit `requests` + `verify=False`.

**HA REST API Calls (für Voice-Status):**

| Zweck | Endpoint | Methode |
|-------|----------|---------|
| Alle Entities (STT/TTS/Wake-Word) | `/api/states` | GET |
| Whisper STT Status | Filter `stt.*` aus `/api/states` (z.B. `stt.faster_whisper`) | - |
| Piper TTS Status | Filter `tts.*` aus `/api/states` (z.B. `tts.piper`) | - |
| openWakeWord Status | Filter `wake_word.*` aus `/api/states` (z.B. `wake_word.openwakeword`) | - |
| Assist Pipelines listen | Kein dedizierter REST-Endpoint; Pipelines über UI/WebSocket | - |

**Hinweis:** Assist Pipelines werden in HA über WebSocket/UI verwaltet. Die REST API liefert nur Entities (stt.*, tts.*, wake_word.*). Der JSON-Report wird nach `data/ha_voice_integration_report.json` geschrieben.

---

### 11. Referenzen

- `src/connectors/home_assistant.py` – CORE HA-Client
- `src/api/routes/ha_webhook.py` – `/webhook/assist`, `/webhook/inject_text`
- `src/voice/tts_dispatcher.py` – TTS an Mini-Speaker
- `docs/03_INFRASTRUCTURE/SCOUT_HA_EVENT_AN_OC_BRAIN.md` – Scout-Events an OMEGA_ATTRACTOR
- [HA Assist Pipeline](https://www.home-assistant.io/integrations/assist_pipeline/)
- [HA Lokale Voice Pipeline](https://www.home-assistant.io/voice_control/voice_remote_local_assistant/)
- `src/scripts/test_ha_voice_integration.py` – Wyoming-Verifizierung


---


<a name="scout-go2rtc-config"></a>
# SCOUT GO2RTC CONFIG

## go2rtc Scout Configuration: MX Brio + Headset
##
## Eintragen in: HA → Add-ons → go2rtc → Konfiguration (YAML)
## oder direkt in die go2rtc.yaml auf dem Scout.
##
## Architektur: Scout hält Hardware, PC konsumiert on demand.
##
## ── Hardware am Scout (Raspi 5) ──
##
##   VIDEO:
##     /dev/video0 = Logitech BRIO (v4l2)
##
##   AUDIO (PulseAudio):
##     Source 4 = alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo   (Brio Mikro, 48kHz Stereo)
##     Source 3 = alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback  (Headset Mikro, 16kHz Mono)
##     Sink   1 = alsa_output.usb-Samsung_USBC_Headset_20190816-00.analog-stereo (Headset Speaker, 44.1kHz)
##
## ── Streams ──
##
##   mx_brio:        Video (Brio) + Audio (Brio-Mikro) → Raumüberwachung
##   headset_mic:    Audio-only (Samsung Headset) → Spracheingabe / Remote-Abhören
##
## ── Szenarien ──
##
##   Passive Raumüberwachung:  PC zieht mx_brio (Video + Audio on demand)
##   Remote Audio-Abruf:       PC zieht headset_mic oder mx_brio Audio
##   Aktive Spracheingabe:     HA Assist Pipeline (Wake Word → Whisper → Ollama → Piper → Headset Speaker)
##                             → Headset-Mikro wird von Assist UND go2rtc parallel genutzt (PulseAudio shared)

streams:
  # Brio: Video + Audio (Raumüberwachung)
  mx_brio:
    - "exec:ffmpeg -f v4l2 -input_format mjpeg -video_size 1920x1080 -i /dev/video0 -f pulse -i alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo -c:v libx264 -preset ultrafast -c:a aac -f rtsp {output}"

  # Headset: Audio-only (Sprache, höhere Qualität für STT)
  headset_mic:
    - "exec:ffmpeg -f pulse -i alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback -c:a aac -f rtsp {output}"

## Video-only Fallback (bewiesen funktionierend, falls exec-Probleme):
## mx_brio: ffmpeg:/dev/video0#video=h264


---


<a name="scout-ha-event-an-oc-brain"></a>
# SCOUT HA EVENT AN OC BRAIN

## Scout (HA auf Raspi): Event an OMEGA_ATTRACTOR senden

Damit der Scout nach Neustart oder bei Sensor-/Kamera-Trigger ein Event an OMEGA_ATTRACTOR schickt, muss HA den VPS-Endpunkt aufrufen.

---

### Copy-Paste (komplett)

**1. Geheimnisse** (Einstellungen → Geheimnisse oder `secrets.yaml`):
- `oc_brain_url`: `https://187.77.68.250` oder `http://187.77.68.250:18789`
- `oc_brain_token`: aus CORE `.env` → `OPENCLAW_GATEWAY_TOKEN`

**2. configuration.yaml** (oder YAML-Add-on):

```yaml
rest_command:
  scout_online_to_oc:
    url: "{{ oc_brain_url }}/v1/responses"
    method: POST
    headers:
      Authorization: "Bearer {{ oc_brain_token }}"
      Content-Type: "application/json"
      x-openclaw-agent-id: "main"
    payload: '{"model":"openclaw","input":"{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"scout_online\",\"priority\":\"low\",\"data\":{}}}"}'

automation:
  - alias: "Scout online → OMEGA_ATTRACTOR"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - delay: "00:01:00"
      - service: rest_command.scout_online_to_oc
```

`oc_brain_url` ohne Port (z. B. `https://187.77.68.250`) → Pfad `/v1/responses` wird angehängt. Mit Port (`http://187.77.68.250:18789`) ebenso.

---

### 1. Token und URL in HA

In **Einstellungen → Geräte & Dienste → Geheimnisse** (oder `secrets.yaml`):

```yaml
oc_brain_url: "http://187.77.68.250:18789"
oc_brain_token: "DEIN_OPENCLAW_GATEWAY_TOKEN"
```

(Bei Nginx-HTTPS: `oc_brain_url: "https://187.77.68.250"` und Port weglassen.)

---

### 2. rest_command in HA

In `configuration.yaml` oder als YAML-Konfiguration:

```yaml
rest_command:
  scout_event_to_oc_brain:
    url: "{{ oc_brain_url }}/v1/responses"
    method: POST
    headers:
      Authorization: "Bearer {{ oc_brain_token }}"
      Content-Type: "application/json"
      x-openclaw-agent-id: "main"
    payload: >
      {
        "model": "openclaw",
        "input": "{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"{{ event_type }}\",\"timestamp\":\"{{ now().isoformat() }}\",\"priority\":\"{{ priority | default('medium') }}\",\"data\":{{ data | default('{}') | tojson }}}"
      }
```

**Hinweis:** `event_type`, `priority`, `data` müssen bei Aufruf übergeben werden (siehe Automation).

---

### 3. Einfacher Aufruf (festes Event)

In `configuration.yaml` (oder YAML-Add-on):

```yaml
rest_command:
  scout_online_to_oc:
    url: "http://187.77.68.250:18789/v1/responses"
    method: POST
    headers:
      Authorization: "Bearer DEIN_OPENCLAW_GATEWAY_TOKEN"
      Content-Type: "application/json"
      x-openclaw-agent-id: "main"
    payload: '{"model":"openclaw","input":"{\"source\":\"scout\",\"node_id\":\"raspi5-ha-master\",\"event_type\":\"scout_online\",\"priority\":\"low\",\"data\":{}}}"}'
```

Token und URL besser in `secrets.yaml`: `oc_brain_url`, `oc_brain_token` – dann `url: !secret oc_brain_url` und `Authorization: "Bearer " + secrets["oc_brain_token"]` (in HA oft als Template).

---

### 4. Automation: Nach Neustart oder manuell

- **Trigger:** Start von Home Assistant (Event `homeassistant_start`) oder ein manueller Schalter.
- **Aktion:** `rest_command.scout_online_to_oc` (oder `scout_event_to_oc_brain` mit Parametern).

Beispiel (Start-Event):

```yaml
automation:
  - alias: "Scout online → OMEGA_ATTRACTOR"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - delay: "00:01:00"
      - service: rest_command.scout_online_to_oc
```

---

### 5. Von 4D_RESONATOR (CORE) aus testen (ohne HA)

```bash
python -m src.scripts.scout_send_event_to_oc --type scout_online --node raspi5-ha-master
```

Damit wird das Event von deinem PC an OMEGA_ATTRACTOR gesendet (gleicher Kanal wie vom Scout).


---


<a name="scout-usb-kamera-mikro-ha-os"></a>
# SCOUT USB KAMERA MIKRO HA OS

## Scout (Raspi 5 + HA OS): USB-Kamera mit Mikro

**Frage:** Kamera (z. B. 4K mit Mikro) per USB am Scout (Raspi 5, Home Assistant OS) – geht das? Scout soll sehen und hören können.

---

### Antwort: Ja, unter Bedingungen

#### Kamera (Video)
- **HA OS** erkennt UVC-USB-Kameras typisch als `/dev/video0`.
- **In HA nutzbar über:**
  - **FFmpeg:** Kamera-Integration mit Eingabe `/dev/video0` (oder passendem Device).
  - **MotionEye-Add-on:** USB-Kamera als „Local V4L2 Camera“ wählen, Stream dann in HA z. B. über Generic Camera.
- Raspi 5 reicht für 4K, ggf. Auflösung/Framerate reduzieren wenn Last hoch ist.

#### Mikro (Audio)
- **HA OS** unterstützt USB-Audio (Mikros) z. B. für **Assist**, **Whisper**, **Piper** (Add-ons).
- **Wichtig:** Ob die **Kamera** Audio liefert, hängt vom Gerät ab:
  - Viele USB-Kameras liefern nur Video (UVC), **kein** Audio.
  - Liefert die Kamera Audio (UAC), erscheint unter Linux ein separates Sound-Device (z. B. in `arecord -l`). Dann kann ein Add-on oder Skript es nutzen.
- Wenn die Kamera **kein** USB-Audio hat: separates USB-Mikro am Raspi (mit Adapter falls nur USB-C) oder Kamera mit Mikro wählen, die UAC unterstützt.

#### Praktisch
1. **Stecker umstecken** (Kamera an Raspi 5).
2. In HA: unter **Einstellungen → System → Hardware** prüfen, ob ein neues Gerät (Video/Audio) erscheint.
3. **Kamera:** Integration hinzufügen (FFmpeg mit `/dev/video0` oder MotionEye).
4. **Mikro:** Wenn ein Audio-Gerät sichtbar ist → z. B. Assist/Whisper konfigurieren oder eigenes Skript; wenn nicht → Kamera liefert kein Audio, dann separates Mikro nötig.

---

### Referenz
- HA OS 12+: Raspi 5 offiziell unterstützt.
- USB-Mikro: z. B. [Community: How to check microphone locally on Rpi5](https://community.home-assistant.io/t/how-to-check-microphone-localy-on-rpi5/697467).
- USB-Kamera: FFmpeg-Integration, MotionEye-Add-on (z. B. `issacg/motioneye-addon`).


---


<a name="scout-wake-word-setup"></a>
# SCOUT WAKE WORD SETUP

## Scout Wake Word & Whisper/Wyoming Setup

**Zweck:** Whisper, Piper und openWakeWord als Wyoming-Integration in Home Assistant einrichten, Assist-Pipeline mit CORE verbinden und Wake Word konfigurieren.

**Voraussetzung:** Add-ons Whisper, Piper, openWakeWord sind installiert und laufen (Scout/Raspi 5).

**Verwandte Docs:**
- [OPENWAKEWORD_MODELS.md](OPENWAKEWORD_MODELS.md) – Verfügbare vordefinierte Modelle
- [CUSTOM_WAKE_WORD_TRAINING.md](CUSTOM_WAKE_WORD_TRAINING.md) – Custom Training für „hey core“ und „computer“

---

### 1. Wyoming-Integration hinzufügen

#### 1.1 Auto-Discovery

Nach dem Start der Add-ons erscheinen die Dienste unter **Einstellungen → Geräte & Dienste → Entdeckt**. Für jede Komponente:

1. **Wyoming (Whisper)** – Configure → Submit
2. **Wyoming (Piper)** – Configure → Submit  
3. **Wyoming (openWakeWord)** – Configure → Submit

#### 1.2 Manuell (falls kein Auto-Discovery)

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. Suche: **Wyoming Protocol**
3. Host: `192.168.178.54` (Scout) oder `homeassistant` (wenn auf HA OS)
4. Port (falls Add-on exponiert):
   - Whisper: 10300
   - Piper: 10200
   - openWakeWord: 10201 (oder Add-on-Dokumentation prüfen)

**Tipp:** In den Add-on-Einstellungen „Netzwerk exponieren“ aktivieren und Port setzen, falls Discovery fehlschlägt.

---

### 2. Assist-Pipeline erstellen

1. **Einstellungen → Sprachassistenten → Assistent hinzufügen**
2. **Name:** z.B. „CORE“
3. **Sprache:** Deutsch (oder gewünschte Sprache)
4. **Conversation Agent:** Home Assistant (Standard) – für CORE-Anbindung siehe Abschnitt 6
5. **Speech-to-Text:** Wyoming (Whisper)
6. **Text-to-Speech:** Wyoming (Piper)
7. **Wake Word:** Wyoming (openWakeWord) – siehe Abschnitt 3
8. **Erstellen** / **Aktualisieren**

---

### 3. Wake Word konfigurieren

#### 3.1 Vordefinierte Wake Words (openWakeWord)

1. **Einstellungen → Sprachassistenten** → Assistent bearbeiten
2. Drei-Punkte-Menü (oben rechts) → **Streaming Wake Word hinzufügen**
3. **Streaming Wake Word Engine:** openwakeword
4. **Wake Word:** z.B. **ok nabu** (zum Testen) oder ein anderes vordefiniertes Modell

**Vordefinierte Modelle:** alexa, hey_mycroft, hey_jarvis, hey_rhasspy, timer, weather.  
**„computer“** und **„core“** sind nicht vordefiniert – siehe [OPENWAKEWORD_MODELS.md](OPENWAKEWORD_MODELS.md) und 3.2.

#### 3.2 Eigenes Wake Word „hey core“ und „computer“

1. [Wake-Word-Training (Google Colab)](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing)
2. `target_word`: `hey core` (oder `core`) bzw. `computer`
3. **Runtime → Run all** ausführen (~30–60 Min.)
4. `.tflite`-Datei herunterladen
5. Samba: `/share/openwakeword` anlegen (falls nicht vorhanden)
6. `.tflite` in `/share/openwakeword` ablegen
7. HA neu starten oder openWakeWord-Add-on neu starten
8. Assistent bearbeiten → Wake Word: eigenes Modell wählen

**Detaillierte Anleitung:** [CUSTOM_WAKE_WORD_TRAINING.md](CUSTOM_WAKE_WORD_TRAINING.md)  
**Dokumentation:** [HA Wake Words erstellen](https://www.home-assistant.io/voice_control/create_wake_word/)

#### 3.3 Zwei Wake Words gleichzeitig (ab HA 2025.10)

Ab Home Assistant 2025.10 unterstützen Voice Satellites **bis zu zwei Wake Words** pro Gerät.  
→ Zwei verschiedene Assistenten/Pipelines mit unterschiedlichen Wake Words (z.B. „hey core“ und „computer“) können parallel aktiv sein.

#### 3.4 Setup-Skripte (CORE)

| Skript | Zweck |
|--------|-------|
| `python src/scripts/download_openwakeword_models.py --all` | Lädt vordefinierte Modelle (hey_jarvis, alexa, etc.) herunter |
| `python src/scripts/setup_scout_wake_words.py -s data/openwakeword_models -t \\\\192.168.178.54\\share\\openwakeword` | Kopiert .tflite nach Scout |

**Ablage auf Scout:** `/share/openwakeword` (Samba: `\\192.168.178.54\share\openwakeword`)

#### 3.5 openWakeWord-Parameter

- **Threshold:** 0.5 (Standard)
- **Trigger Level:** 1 (Standard)
- Bei Fehlauslösungen: Threshold erhöhen (z.B. 0.6–0.7)

---

### 4. Netzwerk-Referenz

| Komponente | IP / Host | Port |
|------------|-----------|------|
| Scout (HA) | 192.168.178.54 | 8123 (HTTPS) |
| 4D_RESONATOR (CORE) (CORE API) | 192.168.178.20 | 8000 (HTTP) |

Scout muss 4D_RESONATOR (CORE) per HTTP erreichen können: `http://192.168.178.20:8000`

---

### 5. configuration.yaml – CORE-Anbindung

#### 5.1 Geheimnisse (empfohlen)

In **Einstellungen → Geheimnisse** oder `secrets.yaml`:

```yaml
core_api_url: "http://192.168.178.20:8000"
core_webhook_token: "778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7"
```

**Hinweis:** `core_webhook_token` = `HA_WEBHOOK_TOKEN` aus `c:\CORE\.env`.

#### 5.2 rest_command.core_assist

```yaml
rest_command:
  core_assist:
    url: "{{ core_api_url }}/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer {{ core_webhook_token }}"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

**Ohne Geheimnisse (nur für Tests):**

```yaml
rest_command:
  core_assist:
    url: "http://192.168.178.20:8000/webhook/assist"
    method: POST
    headers:
      Authorization: "Bearer 778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7"
      Content-Type: "application/json"
    payload: '{"text": {{ text | tojson }}}'
```

#### 5.3 input_text (Workaround)

```yaml
input_text:
  assist_command:
    name: "Assist-Befehl für CORE"
    max: 500
```

#### 5.4 Automation: Text an CORE senden

```yaml
automation:
  - alias: "Assist-Text an CORE senden"
    description: "Leitet Text aus input_text.assist_command an CORE weiter"
    trigger:
      - platform: state
        entity_id:
          - input_text.assist_command
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | length > 0 }}"
    action:
      - service: rest_command.core_assist
        data:
          text: "{{ states('input_text.assist_command') }}"
      - service: input_text.set_value
        target:
          entity_id: input_text.assist_command
        data:
          value: ""
```

**Verwendung:** Text in `input_text.assist_command` setzen (z.B. per Dashboard-Button oder Service-Aufruf) → Automation ruft CORE auf.

---

### 6. Voice-Pipeline → CORE

#### 6.1 Einschränkung

Die Standard-Assist-Pipeline leitet den transkribierten Text an den **Conversation Agent** (z.B. Home Assistant). Es gibt keine direkte Möglichkeit, diesen Text an einen externen Webhook zu schicken.

#### 6.2 Mögliche Ansätze

| Ansatz | Aufwand | Beschreibung |
|--------|---------|--------------|
| **input_text + Button** | Gering | Text manuell eingeben oder per Button setzen → Automation → CORE |
| **assist_pipeline.run_stage Event** | Mittel | Automation auf `assist_pipeline`-Event (z.B. `stt-end`, `intent-start`) – Event-Struktur prüfen |
| **Custom Conversation Agent** | Hoch | Eigene Integration, die an CORE weiterleitet |

#### 6.3 Experimentell: Event-basierte Automation

Falls HA ein Event mit dem transkribierten Text ausgibt:

```yaml
## Beispiel – Event-Namen und Daten je nach HA-Version prüfen
automation:
  - alias: "Assist STT-Text an CORE (experimentell)"
    trigger:
      - platform: event
        event_type: "assist_pipeline.run_stage"
        event_data:
          stage: "stt-end"  # oder "intent-start"
    action:
      - service: rest_command.core_assist
        data:
          text: "{{ trigger.event.data.text | default(trigger.event.data.intent_input) }}"
```

**Hinweis:** Event-Struktur in den Entwicklerwerkzeugen (Ereignisse) prüfen.

#### 6.4 CORE-Verhalten bei /webhook/assist

- CORE führt Triage durch (Befehl vs. Chat/Deep Reasoning)
- Antwort wird per TTS auf dem Mini-Speaker ausgegeben (`tts_dispatcher`, Ziel: `media_player.schreibtisch` oder `TTS_CONFIRMATION_ENTITY`)
- Keine zusätzliche HA-Automation für TTS nötig

---

### 7. Test

#### 7.1 rest_command direkt testen

**Von Scout (SSH) oder einem Gerät im gleichen Netz:**

```bash
curl -X POST http://192.168.178.20:8000/webhook/assist \
  -H "Authorization: Bearer 778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7" \
  -H "Content-Type: application/json" \
  -d '{"text":"Licht an"}'
```

**Erwartung:** `{"status":"ok","action":"voice_processed","reply":"..."}`

#### 7.2 input_text testen

1. **Entwicklerwerkzeuge → Dienste**
2. `input_text.set_value` aufrufen:
   - `entity_id`: `input_text.assist_command`
   - `value`: `Licht an`
3. Automation sollte auslösen und CORE aufrufen

---

### 8. Referenzen

| Thema | Datei / URL |
|-------|-------------|
| openWakeWord Modelle | [OPENWAKEWORD_MODELS.md](OPENWAKEWORD_MODELS.md) |
| Custom Training | [CUSTOM_WAKE_WORD_TRAINING.md](CUSTOM_WAKE_WORD_TRAINING.md) |
| Download-Skript | `src/scripts/download_openwakeword_models.py` |
| Setup-Skript | `src/scripts/setup_scout_wake_words.py` |
| CORE HA-Client | `src/connectors/home_assistant.py` |
| Webhook-Routen | `src/api/routes/ha_webhook.py` – `/webhook/assist`, `/webhook/inject_text` |
| Auth | `src/api/auth_webhook.py` – `verify_ha_auth` (Bearer) |
| TTS | `src/voice/tts_dispatcher.py` |
| Assist-Architektur | [docs/03_INFRASTRUCTURE/SCOUT_ASSIST_PIPELINE.md](SCOUT_ASSIST_PIPELINE.md) |
| HA Voice | [home-assistant.io/voice_control](https://www.home-assistant.io/voice_control/) |
| Wyoming | [home-assistant.io/integrations/wyoming](https://www.home-assistant.io/integrations/wyoming) |
| Wake Words | [home-assistant.io/voice_control/create_wake_word](https://www.home-assistant.io/voice_control/create_wake_word/) |

---

### 9. Codebase-Check (erledigt)

| Prüfung | Ergebnis |
|---------|----------|
| `HA_WEBHOOK_TOKEN` in `.env` | ✅ `778aabf5b13c7b5120161168811908da51448b9435423aacf4b67f31e3bb57e7` |
| Scout IP | ✅ 192.168.178.54 |
| 4D_RESONATOR (CORE) IP | ✅ 192.168.178.20 |
| `/webhook/assist` Endpoint | ✅ `ha_webhook.assist_pipeline` – Payload `{"text": "..."}` |


---


<a name="tampermonkey-tts-integration"></a>
# TAMPERMONKEY TTS INTEGRATION

## CORE TTS Browser-Integration (Tampermonkey)

**Zweck:** Markierten Text im Browser direkt an CORE senden und lokal als Sprache abspielen.

---

### Übersicht

Mit `Strg + Shift + S` wird markierter Text an den lokalen CORE-Backend-Server gesendet, der ihn via ElevenLabs in Sprache umwandelt und auf dem PC abspielt.

```
Browser (Gemini, ChatGPT, etc.)
    ↓ Strg+Shift+S
Tampermonkey GM_xmlhttpRequest (umgeht CORS)
    ↓ POST JSON
http://localhost:8000/api/core/speak
    ↓
ElevenLabs TTS → MP3 → Lokale Wiedergabe (PC-Lautsprecher)
```

---

### 1. Voraussetzung: CORE Backend muss laufen

```batch
START_CORE_DIENSTE.bat
```

Oder manuell:
```powershell
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Backend läuft dann auf: `http://localhost:8000`

---

### 2. Tampermonkey-Skript installieren

1. Tampermonkey Browser-Extension installieren (Chrome/Firefox/Edge)
2. Neues Skript erstellen
3. Folgenden Code einfügen:

```javascript
// ==UserScript==
// @name         CORE TTS Push
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Pusht markierten Text direkt an den lokalen CORE TTS-Server
// @match        https://gemini.google.com/*
// @match        https://chat.openai.com/*
// @match        https://chatgpt.com/*
// @match        https://claude.ai/*
// @match        https://*/*
// @grant        GM_xmlhttpRequest
// @connect      127.0.0.1
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    // === CORE KONFIGURATION ===
    const LOCAL_PORT = 8000;
    const ENDPOINT_URL = `http://127.0.0.1:${LOCAL_PORT}/api/core/speak`;
    
    // Verfügbare Rollen: core_dialog, core_info, therapeut, analyst, core_high_density
    const DEFAULT_ROLE = "core_dialog";

    function pushToCORE(text) {
        GM_xmlhttpRequest({
            method: "POST",
            url: ENDPOINT_URL,
            data: JSON.stringify({ 
                text: text,
                role: DEFAULT_ROLE
            }),
            headers: {
                "Content-Type": "application/json"
            },
            onload: function(response) {
                console.log("CORE-TTS: Wird abgespielt.", response.responseText);
                // Grüner Rahmen = Erfolg
                document.body.style.boxShadow = "inset 0 0 15px #0f0";
                setTimeout(() => document.body.style.boxShadow = "none", 800);
            },
            onerror: function(error) {
                console.error("CORE-TTS Error: Backend nicht erreichbar.", error);
                // Roter Rahmen = Fehler
                document.body.style.boxShadow = "inset 0 0 15px #f00";
                setTimeout(() => document.body.style.boxShadow = "none", 800);
            }
        });
    }

    // Shortcut: STRG + SHIFT + S
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.code === 'KeyS') {
            e.preventDefault(); // Verhindert Browser-Save-Dialog
            
            let selectedText = window.getSelection().toString().trim();
            
            if (selectedText.length > 0) {
                console.log("CORE-TTS: Sende", selectedText.length, "Zeichen...");
                pushToCORE(selectedText);
            } else {
                console.warn("CORE-TTS: Kein Text markiert.");
                // Gelber Rahmen = Warnung
                document.body.style.boxShadow = "inset 0 0 15px #ff0";
                setTimeout(() => document.body.style.boxShadow = "none", 500);
            }
        }
    });
    
    console.log("CORE TTS Push geladen. Shortcut: Strg+Shift+S");
})();
```

4. Speichern (Strg+S)

---

### 3. Nutzung

1. **Backend starten:** `START_CORE_DIENSTE.bat`
2. **Browser öffnen:** Gemini, ChatGPT, Claude, oder beliebige Seite
3. **Text markieren** (mit Maus oder Shift+Pfeiltasten)
4. **Strg + Shift + S** drücken
5. **Audio wird auf PC-Lautsprechern abgespielt**

#### Visuelles Feedback:
- **Grüner Rahmen:** Erfolgreich gesendet, wird abgespielt
- **Roter Rahmen:** Backend nicht erreichbar
- **Gelber Rahmen:** Kein Text markiert

---

### 4. API-Referenz

#### POST `/api/core/speak`
Kurzform - spielt sofort ab.

**Request:**
```json
{
    "text": "Der zu sprechende Text",
    "role": "core_dialog"
}
```

**Response:**
```json
{
    "status": "ok",
    "played": true,
    "path": "c:\\CORE\\media\\tts_abc123.mp3"
}
```

#### POST `/api/core/tts`
Vollversion mit allen Optionen.

**Request:**
```json
{
    "text": "Der zu sprechende Text",
    "role": "core_dialog",
    "state_prefix": "",
    "play": true
}
```

**Parameter:**
| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `text` | string | (required) | Der zu sprechende Text |
| `role` | string | `core_dialog` | Stimme/Rolle aus voice_config |
| `state_prefix` | string | `""` | Emotionaler State-Prefix |
| `play` | bool | `true` | `true` = lokal abspielen, `false` = MP3 zurückgeben |

#### GET `/api/core/voice/roles`
Listet alle verfügbaren Rollen/Stimmen.

**Response:**
```json
{
    "roles": ["core_high_density", "core_info", "core_dialog", "therapeut", "analyst"],
    "roles_with_voice_id": [...]
}
```

---

### 5. Verfügbare Stimmen/Rollen

| Rolle | Beschreibung |
|-------|--------------|
| `core_dialog` | Standard-Konversationsstimme |
| `core_info` | Neutrale Info-Stimme |
| `core_high_density` | Komprimierte, schnelle Ausgabe |
| `therapeut` | Ruhige, empathische Stimme |
| `analyst` | Analytische, sachliche Stimme |

---

### 6. Troubleshooting

#### "Backend nicht erreichbar" (roter Rahmen)
- Prüfen ob Backend läuft: `http://localhost:8000/docs`
- `START_CORE_DIENSTE.bat` ausführen

#### Kein Audio
- ElevenLabs API-Key prüfen (`.env`: `ELEVENLABS_API_KEY`)
- Lautsprecher/Audio-Ausgabe prüfen

#### CORS-Fehler
- Tampermonkey nutzt `GM_xmlhttpRequest`, das CORS umgeht
- Falls trotzdem Fehler: `@connect localhost` und `@connect 127.0.0.1` im Skript-Header prüfen

---

### 7. Erweiterung: Stimme per Shortcut wechseln

Für Power-User: Verschiedene Shortcuts für verschiedene Stimmen:

```javascript
// Strg+Shift+S = core_dialog
// Strg+Shift+T = therapeut  
// Strg+Shift+A = analyst

document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.shiftKey) {
        let role = null;
        if (e.code === 'KeyS') role = 'core_dialog';
        if (e.code === 'KeyT') role = 'therapeut';
        if (e.code === 'KeyA') role = 'analyst';
        
        if (role) {
            e.preventDefault();
            let text = window.getSelection().toString().trim();
            if (text) pushToCORE(text, role);
        }
    }
});
```


---


<a name="voice-pipeline-audio-input-plan"></a>
# VOICE PIPELINE AUDIO INPUT PLAN

## CORE Voice Pipeline – Audio-Input Durchstich

**Problem:** Pipeline konfiguriert (Whisper, Piper, openWakeWord, CORE Conversation), aber **kein Audio-INPUT** erreicht die Assist Pipeline. Brio-Audio ist in go2rtc sichtbar, aber go2rtc liefert nicht an Assist.

---

### 1. Architektur-Entscheidung

#### Kernbefund

| Komponente | Funktion | Audio-Rolle |
|------------|----------|-------------|
| **go2rtc** | RTSP/WebRTC-Stream (Video+Audio) | Konsumiert Brio-Mikro via PulseAudio. **Liefert NICHT an Assist.** |
| **Assist Pipeline** | Wake Word → STT → Agent → TTS | Erwartet Audio von **Wyoming Satellite** (Client-Push). |
| **Assist Microphone Add-on** | Wyoming Satellite auf HA OS | Liest von Host-Mikrofon (PulseAudio/ALSA), streamt an Wyoming. |

**go2rtc und Assist teilen sich keine Pipeline.** go2rtc ist ein Stream-Server; Assist braucht einen **Audio-Client** (Satellite), der PCM an Wyoming sendet.

#### Entscheidung: Weg 1 (produktionsreif)

**Assist Microphone Add-on** installieren und starten. Es nutzt dieselbe Hardware (Brio USB) wie go2rtc – beide lesen von PulseAudio. Kein go2rtc-Umbau nötig.

---

### 2. Implementierungsschritte

#### 2.1 Assist Microphone Add-on prüfen/installieren

**Prüfung (SSH auf Scout oder HA Supervisor API):**

```bash
## Via HA Supervisor API (von 4D_RESONATOR (CORE), mit HASS_TOKEN):
curl -s -H "Authorization: Bearer $HASS_TOKEN" \
  "https://192.168.178.54:8123/api/hassio/addons" | jq '.data.addons[] | select(.slug | contains("assist") or contains("microphone")) | {slug, name, state, version}'
```

**Installation (falls nicht vorhanden):**

1. **Einstellungen → Add-ons → Add-on Store**
2. Suche: **„Assist Microphone“** oder **„Assist“**
3. Add-on **„Assist Microphone“** (core/official) installieren
4. **Starten** und **„Start beim Boot“** aktivieren

**Alternativ via Skript (bereits vorhanden):**

```bash
python install_assist_mic.py
```

> **Hinweis:** `install_assist_mic.py` nutzt `core_assist_microphone`. Falls der Slug abweicht (z.B. `assist_microphone`), in der HA-Add-on-Liste prüfen.

#### 2.2 Assist Microphone mit Pipeline verbinden

1. **Einstellungen → Sprachassistenten**
2. Assistent „CORE“ bearbeiten
3. **Streaming Wake Word** prüfen: openWakeWord + Modell (z.B. „Computer“)
4. **Voice Satellite:** Assist Microphone muss als verbundenes Gerät erscheinen

Falls kein Satellite sichtbar:

- Assist Microphone Add-on neu starten
- HA neu starten
- **Einstellungen → Geräte & Dienste → Wyoming** prüfen – neues Gerät sollte erscheinen

#### 2.3 Audio-Quelle (Brio vs. Headset)

Laut `SCOUT_GO2RTC_CONFIG.md`:

- **Brio:** `alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo`
- **Headset:** `alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback`

Assist Microphone nutzt typisch das **Standard-Eingabegerät**. Auf dem Scout:

1. **Einstellungen → System → Hardware** – prüfen, welches Mikro als Standard gesetzt ist
2. Falls Brio gewünscht: In PulseAudio/ALSA das Brio-Mikro als Default setzen (HA OS: ggf. über Add-on-Konfiguration, falls vorhanden)

**Falls nur Brio angeschlossen:** Sollte automatisch als einziges Mikro genutzt werden.

#### 2.4 Konfiguration Assist Microphone (optional)

In **Add-on → Konfiguration** (falls verfügbar):

```yaml
## Beispiel – exakte Keys je nach Add-on-Version prüfen
mic_volume: 1.0
auto_gain: true
noise_suppression: 1
```

---

### 3. Verifikation

#### 3.1 Satellite-Status

```bash
python check_assist_satellite.py
```

Erwartung: Entities mit `assist`, `satellite`, `microphone`; Wyoming-Devices mit Assist Microphone.

#### 3.2 Voice-Integration-Test

```bash
python -m src.scripts.test_ha_voice_integration
```

#### 3.3 Manueller Pipeline-Test

1. Wake Word sagen (z.B. „Computer“)
2. Befehl sprechen (z.B. „Licht an“)
3. Erwartung: Whisper transkribiert → CORE Conversation → Piper spricht Antwort

---

### 4. Fallback-Optionen

#### Fallback A: Assist Microphone nicht verfügbar / funktioniert nicht

**Wyoming Satellite Add-on** (falls als separates Add-on im Store):

- Äquivalent zu Assist Microphone, evtl. anderer Hersteller (z.B. Rhasspy)
- Installation analog, dann mit Pipeline verbinden

#### Fallback B: RTSP → Wyoming Bridge (Custom)

**Aufwand:** Hoch. **Nur wenn Weg 1 definitiv scheitert.**

1. Skript auf Scout (oder separatem Host): FFmpeg zieht RTSP-Audio von go2rtc
2. PCM-Stream (16 kHz, mono, S16_LE) an Wyoming-Client senden
3. Wyoming-Client-Implementierung erforderlich (z.B. `wyoming-satellite` als Library)

**Einschränkung:** HA OS = kein Root, Add-on-Container. Custom-Skript müsste als Add-on gepackt werden.

#### Fallback C: 4D_RESONATOR (CORE) Voice Satellite (bereits vorhanden)

`src/voice/dreadnought_voice_satellite.py` – nutzt Mikro **am PC**, nicht am Scout.

- **Nicht** für Scout-Brio geeignet
- Nur wenn Voice-Input vom 4D_RESONATOR (CORE)-PC gewünscht ist

#### Fallback D: ESP32/Atom Echo Hardware-Satellite

Physisches Gerät mit Mikro, verbindet sich per Wyoming mit HA. Ersetzt Software-Mikrofon am Scout.

---

### 5. Checkliste (Kurz)

| # | Aktion | Befehl / Ort |
|---|--------|--------------|
| 1 | Assist Microphone installiert? | Einstellungen → Add-ons |
| 2 | Assist Microphone gestartet? | Add-on-Detail → Start |
| 3 | Satellite in Pipeline sichtbar? | Einstellungen → Sprachassistenten |
| 4 | Brio als Mikro erkannt? | System → Hardware |
| 5 | Wake Word + Befehl testen | „Computer“ → „Licht an“ |

---

### 6. Referenzen

- `SCOUT_ASSIST_PIPELINE.md` – Pipeline-Architektur
- `SCOUT_GO2RTC_CONFIG.md` – Brio/Headset PulseAudio-Quellen
- `usb_microphone_research.md` – Assist Microphone als Audio-Input
- `install_assist_mic.py` – Installationsskript
- [HA Voice Control](https://www.home-assistant.io/voice_control/)
- [Wyoming Protocol](https://www.home-assistant.io/integrations/wyoming/)


---


<a name="vps-dienste-und-openclaw-sandbox"></a>
# VPS DIENSTE UND OPENCLAW SANDBOX

## VPS-Dienste-Strategie & OpenClaw-Sandbox

**Kontext:** Der Hostinger-VPS (187.77.68.250) ist ein eigener Server – nicht nur für OpenClaw. Dienste, die auf Pi oder PC ressourcenintensiv oder wartungsintensiv sind, können hier sinnvoll ausgelagert werden. **OpenClaw muss dabei in einer Sandbox laufen** und darf keinen Zugriff auf andere Dienste oder sensible Daten auf demselben Server erhalten.

---

### 1. Welche Dienste sind Auslagerungs-Kandidaten?

| Dienst | Aktuell | Auf VPS sinnvoll? | Begründung |
|--------|---------|-------------------|------------|
| **OpenClaw** | (geplant VPS) | **Ja** | Messenger-Gateway braucht öffentliche Erreichbarkeit; läuft in **Sandbox** (siehe Abschnitt 2). |
| **ChromaDB** | 4D_RESONATOR (CORE) (lokal) / optional VPS | **Ja** | Entlastet 4D_RESONATOR (CORE) (NVMe/I/O); zentrale RAG-DB für CORE; bereits angebunden (`CHROMA_HOST`). |
| **Ollama (leichtere Modelle)** | 4D_RESONATOR (CORE) (i5, GTX 3050) | **Optional** | Kleine Modelle (z. B. für Vorverarbeitung, Routing) könnten auf VPS laufen; **schweres RAG/Osmium bleibt auf 4D_RESONATOR (CORE)** (Datenhoheit, Latenz). |
| **Backup-Ziel / Sync** | aktiv | **Ja** | VPS als externes Backup-Ziel (`/var/backups/core`); `daily_backup.py` pusht von 4D_RESONATOR (CORE) per SFTP; Retention 7 Tage (Cron auf VPS). Siehe [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md). |
| **API-Proxy / Webhook-Empfang** | HA + 4D_RESONATOR (CORE) | **Optional** | Öffentliche URL für Webhooks (z. B. von OpenClaw zu CORE); nur Weiterleitung, keine Logik. |
| **Home Assistant** | Scout (Pi) | **Nein** | Bleibt lokal (Smart Home, Latenz, Datenhoheit). |
| **Ollama (Haupt-Inferenz)** | 4D_RESONATOR (CORE) | **Nein** | GPU + sensible ND-Daten bleiben auf 4D_RESONATOR (CORE). |

**Faustregel:**  
- **VPS:** Öffentlich erreichbare Dienste (OpenClaw, ggf. Webhook-Empfang), zentrale DB (Chroma), Backup-Ziel, optional leichtes Ollama.  
- **4D_RESONATOR (CORE):** Kern-LLM, Chroma-Option lokal, Cursor/Cloud Agents, alle Keys und sensiblen Daten.  
- **Scout (Pi):** HA, Edge, lokale Sensoren/WhatsApp-Webhook zu CORE.

---

### 2. OpenClaw-Sandbox (Pflicht)

OpenClaw verbindet sich mit externen Messengern (WhatsApp, Telegram, …) und leitet Nachrichten weiter. Er darf **keinen Zugriff** auf andere Dienste auf demselben Server haben (kein ChromaDB, kein Ollama, keine .env, keine SSH-Keys).

#### 2.1 Empfohlene Maßnahmen

| Maßnahme | Beschreibung |
|----------|--------------|
| **Docker-Container** | OpenClaw ausschließlich in einem eigenen Container betreiben (offizielles Image bzw. eigenes minimales Image). Kein `--network=host`; nur definierte Ports (z. B. 18789) nach außen. |
| **Eigenes Netzwerk** | Docker-Netzwerk nur für OpenClaw; andere Dienste (Chroma, Ollama) in anderem Netzwerk oder auf localhost des Hosts. OpenClaw erhält keine IPs zu Chroma/Ollama. |
| **Unprivilegierter User** | Container läuft als nicht-root User (wenn das Image/Setup das unterstützt). |
| **Keine Volumes in sensible Bereiche** | Kein Mount von `/root`, `.env`, oder Chroma-Daten in den OpenClaw-Container. Nur Konfiguration für OpenClaw (z. B. `openclaw.json`). |
| **Firewall** | Host-Firewall: Nur nötige Ports (22 SSH, 80/443 optional, 18789 OpenClaw) von außen; intern keine Dienste von OpenClaw zu Chroma/Ollama erreichbar. |
| **Kommunikation CORE ↔ OpenClaw** | Nur von außen (CORE auf 4D_RESONATOR (CORE)/PC) zum OpenClaw-Gateway (HTTPS/HTTP); OpenClaw ruft nicht zurück auf den Rest des Servers. |

#### 2.2 Architektur-Skizze (VPS)

```
[Internet]
    │
    ├──► [OpenClaw-Container]  Port 18789  (Sandbox, nur dieser Dienst)
    │         │
    │         └──► Nachrichten nur an externe CORE-URL (z. B. Webhook auf 4D_RESONATOR (CORE)/NGROK)
    │
    └──► [ChromaDB]  Port 8000  (nur von CORE/vertrauenswürdigen Clients)
    └──► [optional: Ollama light]  Port 11434  (nur intern oder nur für CORE)
```

OpenClaw hat **keine** Verbindung zu ChromaDB oder Ollama auf demselben Host; alle LLM-/RAG-Anfragen gehen von CORE (lokal) aus, das ggf. ChromaDB auf dem VPS per `CHROMA_HOST` anspricht.

#### 2.3 Checkliste vor Go-Live

- [ ] OpenClaw läuft in eigenem Docker-Container (kein Zugriff auf Host-Dateisystem außer OpenClaw-Config).
- [ ] Kein gemeinsames Docker-Netzwerk mit ChromaDB/Ollama; oder Chroma/Ollama nicht im selben Netzwerk wie OpenClaw.
- [ ] Firewall: Keine eingehenden Verbindungen von OpenClaw-Container zu anderen Ports auf dem Host.
- [ ] CORE ruft OpenClaw-Gateway von außen auf (Token in .env); OpenClaw leitet nur an konfigurierte Webhook-URLs weiter.

---

### 3. Bei Hostinger umsetzen (konkrete Schritte)

Folgende Dinge sind **auf dem VPS (187.77.68.250)** umzusetzen, damit die Dienste aus Abschnitt 1 laufen und OpenClaw sandboxed bleibt.

#### 3.1 Basis (einmalig)

| Schritt | Aktion |
|--------|--------|
| SSH | `ssh root@187.77.68.250` (Zugang aus CORE .env: VPS_HOST, VPS_USER, VPS_PASSWORD). |
| Firewall | Nur nötige Ports von außen öffnen: 22 (SSH), 80/443 (optional), 18789 (OpenClaw), 8000 (ChromaDB nur wenn von außen nötig). Chroma/Ollama ideal nur localhost oder über SSH-Tunnel. |
| Docker | Falls noch nicht installiert: Docker installieren (z. B. `curl -fsSL https://get.docker.com | sh`), damit OpenClaw und ggf. Chroma im Container laufen. |

#### 3.2 OpenClaw (in Sandbox)

| Schritt | Aktion |
|--------|--------|
| 1 | Eigenes Docker-Netzwerk anlegen: `docker network create openclaw_net` (nur für OpenClaw). |
| 2 | OpenClaw-Container **ohne** Mount von `/root` oder Host-Config außer der OpenClaw-Konfiguration starten. Nur Port 18789 nach außen mappen. Kein `--network=host`. |
| 3 | OpenClaw so konfigurieren, dass er nur an konfigurierte Webhook-URLs (z. B. CORE-Core-URL/NGROK) weiterleitet – keine internen Host-URLs (kein localhost:8000 für Chroma, kein localhost:11434). |
| 4 | In CORE .env: `OPENCLAW_GATEWAY_TOKEN` und `VPS_HOST` gesetzt; Test mit `check_gateway()` aus `openclaw_client` sobald OpenClaw läuft. |

#### 3.3 ChromaDB

| Schritt | Aktion |
|--------|--------|
| 1 | Chroma läuft im Container `chroma-core`; **gebunden an 127.0.0.1:8000** (nicht öffentlich). |
| 2 | **Zugriff von außen:** Nur per SSH-Tunnel, z. B. `ssh -L 8000:127.0.0.1:8000 root@VPS_HOST`. Dann in .env: `CHROMA_HOST=localhost`, `CHROMA_PORT=8000`. |
| 3 | Ingest von 4D_RESONATOR (CORE) aus (wenn Tunnel aktiv): `python src/scripts/ingest_nd_insights_to_chroma.py`. |

#### 3.4 Backup-Ziel (aktiv)

| Schritt | Aktion |
|--------|--------|
| 1 | Verzeichnis `/var/backups/core` wird von `setup_vps_hostinger.py` angelegt; Cron löscht Backups älter als 7 Tage. |
| 2 | **daily_backup.py** (auf 4D_RESONATOR (CORE)) pusht täglich per SFTP; Aufruf per Task Scheduler (Windows) oder cron. Siehe [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md). |
| 3 | Der VPS pullt nicht; nur Push von CORE aus. |

#### 3.5 Optional: leichtes Ollama, Webhook-Proxy

- **Ollama (leicht):** Nur wenn gewünscht – kleines Modell auf dem VPS installieren, Port 11434 nur für CORE-IP oder über Tunnel erreichbar halten. Schweres RAG/Osmium bleibt auf 4D_RESONATOR (CORE).
- **Webhook-Proxy:** Nginx/Caddy auf dem VPS, der nur bestimmte Pfade (z. B. `/webhook/openclaw`) an deine CORE-URL (NGROK oder DynDNS) weiterleitet; keine Logik auf dem VPS.

#### 3.6 Übersicht: Ports auf dem VPS

| Port | Dienst | Von außen? |
|------|--------|-------------|
| 22 | SSH | Ja (für Admin) |
| 18789 | OpenClaw | Ja (Messenger-Gateway) |
| 8000 | ChromaDB | Nur 127.0.0.1 auf VPS; Zugriff von außen nur per SSH-Tunnel |
| 80/443 | Nginx/Caddy (optional) | Optional (Webhook-Proxy, Let’s Encrypt) |

---

### 4. Referenzen

- **Schnittstellen:** OpenClaw, ChromaDB, Go2RTC, .env – siehe [BACKUP_PLAN_FINAL.md](BACKUP_PLAN_FINAL.md) und [VPS_FULL_STACK_SETUP.md](VPS_FULL_STACK_SETUP.md).
- **Hardware:** [01_ARCHITEKTUR_HARDWARE_OSMIUM.md](../../data/antigravity_docs_osmium/01_ARCHITEKTUR_HARDWARE_OSMIUM.md) (4D_RESONATOR (CORE), Scout).
- **OpenClaw Docs:** https://docs.openclaw.ai/
- **Go2RTC (Kamera PC):** [CAMERA_GO2RTC_WINDOWS.md](CAMERA_GO2RTC_WINDOWS.md).


---


<a name="vps-full-stack-setup"></a>
# VPS FULL STACK SETUP

## VPS Full-Stack Setup - CORE/SHELL

**Deploy-Skript:** src/scripts/deploy_vps_full_stack.py

---

### Was wird deployed?

| Container | Port | Netzwerk | Funktion |
|---|---|---|---|
| homeassistant | 18123 | core_net | Home Assistant Docker; Remote HA nach Scout |
| openclaw-admin | 18789 | core_net | OC Gehirn; Gemini 3.1 Pro, Claude 4.6, Nexos, WhatsApp |
| openclaw-spine | 18790 | core_net | OC Spine; sauberes System, nutzt admin als Gateway |

### Netzwerk-Isolation

| Netzwerk | Typ | Zugriff |
|---|---|---|
| core_net | bridge | Internet (Gemini/Anthropic/Nexos-APIs), Kommunikation zwischen Containern |

*(Hinweis: Die alte Aufsplittung in separate openclaw_admin_net, openclaw_spine_net und chroma_net wurde zugunsten eines übersichtlichen `docker-compose` mit `core_net` vereinfacht. Eine separate chroma-core Instanz entfällt, da `chroma-uvmy` genutzt wird.)*

### Firewall (ufw)

Offen: 22/tcp, 18789/tcp, 18790/tcp, 18123/tcp, 443/tcp, 80/tcp.
Geblockt: 8000/tcp (ChromaDB nur intern).

---

### Deploy ausfuehren

    # Dry-run (kein SSH, nur Ausgabe):
    python -m src.scripts.deploy_vps_full_stack --dry-run

    # Echtes Deployment:
    python -m src.scripts.deploy_vps_full_stack

    # Ohne HA-Container:
    python -m src.scripts.deploy_vps_full_stack --skip-ha

    # Ohne Extraktion des alten VPS:
    python -m src.scripts.deploy_vps_full_stack --skip-extract

---

### Benoetiate .env-Variablen

    OPENCLAW_ADMIN_VPS_HOST=<IP>
    OPENCLAW_ADMIN_VPS_USER=root
    OPENCLAW_ADMIN_VPS_PASSWORD=...
    GEMINI_API_KEY=...
    ANTHROPIC_API_KEY=...
    NEXOS_API_KEY=...          (optional)
    OPENCLAW_GATEWAY_TOKEN=... (Admin)
    OPENCLAW_SPINE_TOKEN=...   (optional)
    HA_VPS_PORT=18123
    HA_URL=http://192.168.178.54:8123
    HA_TOKEN=eyJ...

---

### Naechste Schritte nach dem Deploy

1. HA Ersteinrichtung: http://<VPS_HOST>:18123
2. HACS installieren: https://hacs.xyz/docs/setup/download
3. Remote Home Assistant: HACS -> Remote Home Assistant -> HA neu starten
4. Scout HA erreichbar machen:
   Option A: Nabu Casa (HA Cloud) -> oeffentliche URL
   Option B: Reverse-SSH-Tunnel von Scout:
             autossh -M 0 -R 18124:localhost:8123 root@<VPS_HOST> -N -f
5. OpenClaw Admin testen: curl http://<VPS_HOST>:18789/api/status
6. OpenClaw Spine befuellen: python -m src.scripts.check_openclaw_config_vps
7. CORE .env ergaenzen:
   OPENCLAW_ADMIN_VPS_HOST=<VPS_HOST>
   OPENCLAW_GATEWAY_PORT=18789
   HA_VPS_URL=http://<VPS_HOST>:18123

---

### Referenzen

- OPENCLAW_ADMIN_ARCHITEKTUR.md
- PROJEKT_ANNAHMEN_UND_KORREKTUREN.md
- NEXOS_EINBINDUNG.md
- OPENCLAW_GATEWAY_TOKEN.md


---


<a name="vps-ip-monitoring"></a>
# VPS IP MONITORING

## VPS IP-Monitoring und Automatisierung

**Stand:** 2026-03-04

---

### Problem: Dynamische VPS-IP bei Hostinger

Hostinger VPS (KVM) haben **keine garantiert statische IP**. Die IP kann sich ändern bei:

1. **VPS-Neustart** (selten, aber möglich)
2. **Hostinger-Wartung** (Datacenter-Migration)
3. **Manueller Neustart via Panel**

**Beobachtung 2026-03-02 → 2026-03-04:**
- IP war `187.77.68.250`
- Danach Timeout bei SSH → IP hat sich geändert

---

### Auswirkungen

| Betroffenes System | Symptom |
|---|---|
| `.env` (`VPS_HOST`, `OPENCLAW_ADMIN_VPS_HOST`) | SSH-Verbindung schlägt fehl |
| ChromaDB-Sync | Tunnel kann nicht aufgebaut werden |
| OpenClaw Gateway | API nicht erreichbar |
| Dokumentation | Veraltete IP-Referenzen |

---

### Lösung: Automatisches IP-Monitoring

#### Option A: Hostinger API (empfohlen)

Hostinger bietet eine API zum Abrufen der aktuellen VPS-IP:

```bash
## API-Key im Hostinger Panel unter "API-Zugang" generieren
curl -H "Authorization: Bearer $HOSTINGER_API_KEY" \
  https://api.hostinger.com/v1/vps/{server_id}
```

**TODO:** Hostinger API-Key generieren und in `.env` als `HOSTINGER_API_KEY` hinterlegen.

#### Option B: DuckDNS für VPS (einfach)

VPS registriert seine IP automatisch bei DuckDNS:

```bash
## Auf VPS als Cron-Job (alle 5 Min):
*/5 * * * * curl -s "https://www.duckdns.org/update?domains=core-vps&token=$DUCKDNS_TOKEN&ip="
```

Dann in `.env`:
```
VPS_HOST="core-vps.duckdns.org"
```

**Vorteil:** IP-Änderung wird automatisch propagiert, keine manuelle Anpassung nötig.

#### Option C: Manuell (aktueller Stand)

1. Im Hostinger Panel einloggen
2. VPS → Übersicht → IP-Adresse kopieren
3. `.env` aktualisieren (`VPS_HOST`, `OPENCLAW_ADMIN_VPS_HOST`)
4. Dokumentation mit neuer IP aktualisieren

---

### Skript: IP-Check und .env-Update

```python
## src/scripts/check_vps_ip.py
## TODO: Implementieren wenn Hostinger API-Key vorhanden
```

---

### Empfehlung

**Kurzfristig:** Option C (manuell) – aktuelle IP im Hostinger Panel prüfen und `.env` aktualisieren.

**Mittelfristig:** Option B (DuckDNS) – einmalig auf VPS einrichten, dann automatisch.

**Langfristig:** Option A (Hostinger API) – vollautomatisch mit Health-Monitoring.

---

### Daten-Sicherheit bei IP-Wechsel

Die Daten auf dem VPS bleiben **erhalten**. Der IP-Wechsel betrifft nur die Netzwerk-Adresse, nicht den Storage. Docker-Volumes (`chroma_data`, etc.) sind persistent.

**Prüfung nach IP-Wechsel:**
1. SSH auf VPS mit neuer IP
2. `docker ps` – Container sollten noch laufen
3. `docker volume ls` – Volumes intakt
4. ChromaDB-Sync ausführen zur Bestätigung

---

### Referenzen

- `docs/04_PROCESSES/STANDARD_AKTIONEN_UND_NACHSCHLAG.md`
- `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md`


---


<a name="vps-slim-deploy"></a>
# VPS SLIM DEPLOY

## VPS-Slim Deployment

**Ziel:** Scout-Forwarded-Text bei HA-Ausfall auf VPS verarbeiten.

| Parameter | Wert |
|-----------|------|
| VPS | 187.77.68.250 |
| SSH Key | `c:\CORE\.ssh\id_ed25519_hostinger` |
| User | root |
| Port | 8001 |

### Voraussetzungen

- CORE `src/` inkl. Abhängigkeiten (core_llm, HAClient, logic_core.context_injector)
- `.env` mit: `HA_WEBHOOK_TOKEN`, `GEMINI_API_KEY`, `HA_URL`, `HA_TOKEN`, `CHROMA_HOST` (optional)

### Automatischer Deploy (empfohlen)

```powershell
## .env: VPS_HOST=187.77.68.250, VPS_USER=root, VPS_SSH_KEY=c:\CORE\.ssh\id_ed25519_hostinger
python -m src.scripts.deploy_vps_slim
```

Kopiert `src/` + `Dockerfile.vps`, baut Docker-Image, startet Container auf Port 8001. Benötigt `.env` auf VPS unter `VPS_DEPLOY_PATH` (default `/opt/core-core`).

### Manueller Deploy

```powershell
## 1. SSH-Verbindung testen
ssh -i c:\CORE\.ssh\id_ed25519_hostinger root@187.77.68.250 "echo OK"

## 2. Code + .env auf VPS kopieren (tar+scp wie deploy_agi_state.py)
## Oder: python -m src.scripts.deploy_vps_slim

## 3. Auf VPS: Service starten
ssh -i c:\CORE\.ssh\id_ed25519_hostinger root@187.77.68.250
cd /opt/core-core
source .venv/bin/activate  # oder: python -m venv .venv && pip install -r src/requirements.txt
VPS_SLIM_PORT=8001 python -m uvicorn src.api.vps_slim:app --host 0.0.0.0 --port 8001
```

### systemd (empfohlen)

```ini
## /etc/systemd/system/core-vps-slim.service
[Unit]
Description=CORE VPS-Slim Failover
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/core-core
EnvironmentFile=/opt/core-core/.env
ExecStart=/opt/core-core/.venv/bin/python -m uvicorn src.api.vps_slim:app --host 0.0.0.0 --port 8001
Restart=unless-stopped

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable core-vps-slim
sudo systemctl start core-vps-slim
```

### Firewall

```bash
ufw allow 8001/tcp
ufw reload
```

### Health-Check

```bash
curl http://187.77.68.250:8001/
## Erwartet: {"status":"online","system":"CORE_VPS_SLIM","version":"1.0.0"}
```

### Scout-Konfiguration

Scout/core_conversation Failover-URL: `http://187.77.68.250:8001/webhook/forwarded_text`  
Header: `Authorization: Bearer <HA_WEBHOOK_TOKEN>`


---


<a name="whatsapp-e2e-ha-setup"></a>
# WHATSAPP E2E HA SETUP

## WhatsApp E2E von HA – Setup und Ablauf

Damit der komplette Weg **Nachricht → HA → CORE → Antwort im Chat** funktioniert, müssen in HA zwei Dinge stehen: **rest_command** (ruft CORE auf) und **Automation** (reagiert auf das WhatsApp-Event).

**Ablauf:** Du startest CORE **einmal** (z.B. mit `START_CORE_KOMPLETT.bat` beim Anmelden oder Tagesstart). Ab dann triggert **die eingehende @Core-Nachricht** die Kette – nicht du vor jeder WhatsApp. Optional: Autostart (siehe [WIEDER_DA_ALLES_LAEUFT.md](../05_AUDIT_PLANNING/WIEDER_DA_ALLES_LAEUFT.md) Abschnitt 6), dann ist CORE bereit sobald der Rechner läuft.

---

### 1. rest_command in HA

CORE muss von HA aus per HTTP erreichbar sein (4D_RESONATOR (CORE) oder Scout, z. B. `http://192.168.178.20:8000`). In `configuration.yaml` (oder über die HA-Oberfläche → Einstellungen → Geräte & Dienste → REST-Befehle):

```yaml
rest_command:
  core_whatsapp_webhook:
    url: "http://DEINE_CORE_IP:8000/webhook/whatsapp"
    method: POST
    content_type: "application/json"
    payload: '{{ payload | tojson }}'
    timeout: 15
```

- **DEINE_CORE_IP** durch die IP des Rechners ersetzen, auf dem die CORE-CORE-API läuft (z. B. 4D_RESONATOR (CORE)), oder die des Scouts, falls CORE dort läuft.
- **timeout: 15** (Sekunden): CORE antwortet bei Chat/Reasoning sofort mit HTTP 202; 15s reichen. Ohne Angabe nutzt HA 10s – ausreichend, da keine lange Wartezeit mehr im Request.
- Der Aufruf übergibt den Schlüssel **payload**; der Wert (Addon-Event-Daten) wird als JSON an CORE gesendet.

Falls du eine Konfiguration über die UI nutzt: Der REST-Befehl soll **POST** an `http://CORE_IP:8000/webhook/whatsapp` senden, Body = JSON aus dem übergebenen **payload**.

---

### 2. Automation in HA

Bei jeder eingehenden WhatsApp-Nachricht (Addon feuert Event) soll der rest_command mit den Event-Daten aufgerufen werden. Beispiel (YAML oder in der Automations-UI):

```yaml
- alias: "CORE: Weiterleitung WhatsApp eingehend"
  trigger:
    - platform: event
      event_type: whatsapp_message_received
  action:
    - service: rest_command.core_whatsapp_webhook
      data:
        payload: "{{ trigger.event.data }}"
```

- **event_type** ggf. anpassen, falls das Addon ein anderes Event nutzt (z. B. `new_whatsapp_message` o. ä.). In den Addon-Dokumenten oder unter Entwicklerwerkzeuge → Ereignisse nachsehen.

Das Skript **wire_whatsapp_ha.py** kann diese Automation in die HA-Config eintragen (per SSH auf den Scout); danach HA-Konfiguration neu laden.

---

### 2.1 Routing: @Core und @OC (nur Adressierter reagiert)

Damit nicht auf **jede** WhatsApp-Nachricht automatisch geantwortet wird:

- **Nachricht beginnt mit @Core** → CORE/Scout verarbeiten (Antwort mit **[CORE]** bzw. **[Scout]**). Präfix wird vor der Verarbeitung abgezogen.
- **Nachricht beginnt mit @OC** → nur für OC; CORE reagiert **nicht** (ignoriert).
- **Weder @Core noch @OC am Anfang** → CORE reagiert nicht.
- **@Core am Anfang, @OC später in der Nachricht** → Teil für beide; CORE verarbeitet seinen Teil, OC den nach @OC.

Details (inkl. OC-Prozedere und Antwortformat [CORE]/[OC]): **docs/WHATSAPP_ROUTING_CORE_OC.md**.

---

### 3. E2E-Test ausführen

**Voraussetzungen:** HA erreichbar, rest_command und Automation wie oben eingerichtet, CORE-CORE-API läuft und ist von HA aus erreichbar.

```bash
cd C:\CORE
python -m src.scripts.run_whatsapp_e2e_ha
```

Das Skript ruft den HA-Service **rest_command.core_whatsapp_webhook** mit einem addon-ähnlichen Payload auf (Absender = WHATSAPP_TARGET_ID aus .env, Nachricht = "E2E-Test von HA: Ping"). Damit durchläuft die gleiche Kette wie bei einer echten Nachricht: HA → CORE → Antwort per **send_whatsapp** → HA whatsapp/send_message. Wenn alles stimmt, erscheint die CORE-Antwort im Chat zu WHATSAPP_TARGET_ID (in der Regel dein eigener Chat).

---

### 4. Echte Nachricht (manueller E2E)

1. Von einem Gerät eine WhatsApp-Nachricht in einen Chat senden, der auf dem mit dem HA-Addon verbundenen Account ankommt (z. B. an dich selbst).
2. Addon löst Event aus → Automation → rest_command → CORE.
3. CORE antwortet über HA an den Absender; die Antwort erscheint im selben Chat.

---

### 5. Präfix [CORE] und [Scout] in Nachrichten

Jede **von CORE/Scout ausgelöste** WhatsApp-Antwort beginnt mit einem Präfix, damit erkennbar ist, woher die Nachricht kommt:

- **[CORE]** – Nachricht vom **4D_RESONATOR (CORE)** (volles Modell): tiefere Reasoning-Antworten, Chat, Sprachanalyse-Ergebnis.
- **[Scout]** – Nachricht vom **kleinen Modell / direkter Steuerung**: z. B. Bestätigung von HA-Steuerbefehlen („Licht an“, „Szene XY“), „Nicht verstanden“, oder kurze Systembestätigungen („Sprachmemo empfangen …“).

Implementierung: `src/api/routes/whatsapp_webhook.py` setzt den Präfix je nach Intent (command → [Scout], deep_reasoning/chat + Audio-Ergebnis → [CORE]).

---

### 6. Abgrenzung zu OpenClaw (OC)

OC (OpenClaw) hat einen **eigenen** WhatsApp-Kanal (Gateway mit Baileys auf dem VPS). Das ist ein **zweiter** Weg, unabhängig von HA. Der **HA-E2E** betrifft nur den Pfad über deinen Account + Addon + CORE. Siehe [WHATSAPP_OPENCLAW_VS_HA.md](../02_ARCHITECTURE/WHATSAPP_OPENCLAW_VS_HA.md).

---

### 7. Troubleshooting (Hänger / Timeout / „dreht minutenlang“)

| Symptom | Ursache | Maßnahme |
|--------|---------|---------|
| Verbindung dreht minutenlang, bricht ab, danach wieder „warten“ | HA **rest_command** wartet auf CORE-Antwort; Default-Timeout 10s. Früher: CORE führte LLM (30s+) synchron aus → HA brach ab. | CORE antwortet bei Chat/Reasoning sofort mit **HTTP 202** und verarbeitet im Hintergrund. rest_command mit `timeout: 15` reicht. Doku oben prüfen. |
| Keine Antwort im Chat | CORE-API von HA aus nicht erreichbar (Netz/Firewall, falsche IP). | `url` in rest_command prüfen (http://CORE_IP:8000). Von HA-Host aus: `curl -X POST http://CORE_IP:8000/webhook/whatsapp -H "Content-Type: application/json" -d '{}'` → erwartet 200/202 oder JSON. |
| 4xx von CORE | Falsches Payload-Format (z. B. fehlendes `message`/`key.remoteJid`). | Automation muss `payload: "{{ trigger.event.data }}"` übergeben. Addon-Event-Struktur in HA unter Entwicklerwerkzeuge → Ereignisse prüfen. |
| WhatsApp-Nachricht geht nicht raus (CORE → HA) | HA-Service `whatsapp/send_message` nicht erreichbar oder Timeout. | HASS_URL/HASS_TOKEN in .env. CORE nutzt 15s Timeout für send_whatsapp. HA-Logs und Addon-Status prüfen. |

**E2E-Test (schnell prüfbar):**

```bash
cd C:\CORE
python -m src.scripts.run_whatsapp_e2e_ha
```

Erwartung: Exit 0, in den CORE-Logs „WhatsApp Webhook“ bzw. „text_handled“/„text_queued“, und eine Antwort im Chat (z. B. „[Scout] …“ oder „[CORE] …“).


---


<a name="google-assistant-ollama-research"></a>
# google assistant ollama research

## Google Assistant to Home Assistant/Ollama Integration Notes

### The Goal
Use a Google Home Mini ("Hey Google") to capture a voice command, send the transcribed text to Home Assistant, process it locally with Ollama, and have the Google Home Mini speak the response.

### The Reality (2024-2025)
**Direct interception is currently NOT possible using software alone.**

#### Nabu Casa vs Manual Integration
It does not matter whether you use Nabu Casa (Home Assistant Cloud) or set up the manual Google Assistant integration (using Google Cloud Console and setting up your own OAuth/fulfillment). 

Both methods share the same limitation:
The integration *only* allows Google Assistant to control Home Assistant devices (e.g., "Hey Google, turn on the living room light"). 
Home Assistant **cannot** intercept the raw audio or the text of what you say to the Google Mini. Google processes the voice and determines the intent. You cannot route custom conversational text directly to Ollama through the Mini's microphone using official APIs.

### Alternatives and Workarounds

#### 1. Modifying the Google Mini Hardware (Advanced/DIY)
Project **Onju Voice**: A community hardware project where you open up a Google Nest Mini, rip out the Google PCB, and install a custom ESP32 board. This completely removes Google from the device and turns it into a dedicated, local Home Assistant voice satellite while keeping the nice speaker/case.

#### 2. Dedicated Local Voice Satellites (The recommended Home Assistant way)
Instead of using the Google Mini's microphone, the modern Home Assistant approach uses dedicated, open hardware.
- **Hardware:** Build or buy an ESP32-based "Voice Satellite" (like the Atom Echo, ESP32-S3-BOX). 
- **Flow:** "Hey Jarvis" -> ESP32 Satellite -> Home Assistant (Whisper) -> **Ollama LLM** -> Home Assistant (Piper) -> ESP32 Satellite Speaker.

### Conclusion
To use Ollama as a voice assistant, you will need to invest in a local voice satellite device (ESP32-based) rather than trying to software-hack the Google Mini ecosystem. The Google Mini can still be used as an output speaker to play sounds generated by HA, but it cannot act as the microphone.


---


<a name="usb-microphone-research"></a>
# usb microphone research

## USB Microphone Integration for Home Assistant

### Feasibility
**Yes, absolutely!** Plugging a USB microphone directly into your Raspberry Pi running Home Assistant OS is a fully supported and excellent way to achieve local voice control with Ollama.

This bypasses Google entirely and keeps your voice processing 100% local and private.

### How it Works (The "Assist" Pipeline)
When you plug a USB mic into the Pi, Home Assistant doesn't inherently know what to do with the audio. You need to set up a "Voice Pipeline" using the Wyoming protocol.

The pipeline looks like this:
1. **Audio Input:** USB Microphone -> "Assist Microphone" Add-on
2. **Wake Word Detection (Optional but recommended):** "OpenWakeWord" Add-on (listens for "Hey Jarvis" or "Okay Nabu").
3. **Speech-to-Text (STT):** "Whisper" Add-on (converts your audio to text).
4. **Processing (The Brain):** **Ollama** Integration (reads the text, decides what to do, generates a text response).
5. **Text-to-Speech (TTS):** "Piper" Add-on (converts Ollama's text back into audio).
6. **Audio Output:** Played through the 3.5mm jack on the Pi, a USB speaker, or cast to a media player (like your `media_player.schreibtisch` Google Mini!).

### Steps to Implement
1. **Plug in the Mic:** Connect your USB microphone to the Raspberry Pi.
2. **Install Add-ons (via Settings -> Add-ons):**
   - **Assist Microphone:** To capture the audio.
   - **Whisper:** For Speech-to-Text.
   - **Piper:** For Text-to-Speech.
   - **OpenWakeWord:** For hands-free activation.
3. **Configure Voice Assistant:** Go to Settings -> Voice Assistants and create a new pipeline that uses Whisper, Piper, and your Ollama conversation agent.

### Hardware Considerations
- **Raspberry Pi 4 Performance:** A Pi 4 can run Whisper and Piper, but it will be slightly slow (a few seconds delay between speaking and the response). 
- **Ollama Performance:** You are already pulling `llama3.1`. Running an LLM *and* voice processing tools on a single Raspberry Pi will be very heavy. Responses might take 10-30 seconds depending on the model size and quantization. 

### Recommended USB Microphones
- Jabra Speak 410/510 (Excellent because it includes a speaker and great echo cancellation).
- Seeed ReSpeaker USB Mic Array.
- Almost any standard plug-and-play USB webcam/desk microphone will work for basic testing.


---

# Kamera-Anbindung: go2rtc (Windows / Scout)

ATLAS_CORE kann Kamerabilder über go2rtc beziehen. go2rtc läuft entweder **auf dem PC** (Windows, z.B. Logitech Brio) oder **auf dem Scout (Pi)** – letzteres ist oft stabiler.

---

## Webcam vs. Überwachungskamera (warum die Brio „nicht immer läuft“)

- **Überwachungs-/IP-Kamera:** Läuft dauerhaft, streamt 24/7, LED oft dauerhaft an. Typisch für go2rtc auf dem **Scout** (Pi-Kamera oder USB-Kamera am Pi).
- **Webcam (z.B. Logitech Brio):** Ist für **On-Demand** ausgelegt – sie überträgt nur, wenn eine Anwendung sie explizit anspricht und Frames anfordert. Dauerstream ist nicht das typische Nutzungsprofil; die LED bleibt oft aus, wenn kein Programm die Kamera hält.

Für ATLAS reicht in der Regel **ein Snapshot bei Bedarf** (z.B. ein Bild pro Anfrage). Dafür muss die Kamera nicht dauerhaft laufen. Zwei Wege:

1. **go2rtc (PC oder Scout):** Wenn ein Stream konfiguriert ist, liefert die Snapshot-API (`/api/frame.jpeg?src=...`) bei jedem Aufruf ein aktuelles Bild – go2rtc hält dabei ggf. den Stream kurz an. Beim Scout ist der Stream oft dauerhaft aktiv (Kamera am Pi); am PC mit Brio kann der Stream bei reiner On-Demand-Nutzung zwischen den Abrufen ruhen oder über einen **On-Demand-Snapshot-Server** (siehe unten) abgedeckt werden.
2. **On-Demand-Snapshot-Server (nur Brio/PC):** Ein kleiner Dienst, der **nur bei einem HTTP-Aufruf** (z.B. GET /snapshot.jpg) die Webcam kurz öffnet, ein Einzelbild liefert und wieder schließt – LED nur während des Abrufs. Siehe Abschnitt „On-Demand-Snapshot für die Brio (PC)“.

### MX (Brio) als Überwachungskamera: Dauerstream

Wenn du die Brio **wie eine Überwachungskamera** nutzen willst (ständig Bild für Erkennung/Brio-Szenario), ist es **kein Problem**, den Stream **dauerhaft laufen zu lassen**. Du kannst go2rtc mit dem Brio-Stream einfach durchlaufen lassen – die Kamera bleibt dann aktiv (LED an), und ATLAS (z.B. `brio_scenario_periodic.py` oder Snapshot-Abfragen) bekommt jederzeit ein aktuelles Bild. Ein gezieltes An- und Abschalten ist nicht nötig; wenn du den Dauerbetrieb möchtest, starte go2rtc mit der Brio-Konfiguration und lasse ihn laufen. Siehe Abschnitt „Logitech Brio (MX) unter Windows einbinden“ für die go2rtc-Einrichtung.

---

## Alternative: go2rtc auf dem Scout (empfohlen, wenn PC-Stream Probleme macht)

Auf dem **Scout (Raspberry Pi)** läuft go2rtc bereits und funktioniert ohne Probleme. Statt die Brio am PC zu nutzen, kannst du den Kamera-Stream **über den Scout** abgreifen:

1. **Scout-IP oder Hostname** ermitteln (z.B. `192.168.2.x` oder `scout.local`).
2. In der **ATLAS_CORE .env** setzen:
   - `GO2RTC_BASE_URL=http://<scout-ip>:1984` (z.B. `http://192.168.2.10:1984` oder `http://scout.local:1984`)
   - `GO2RTC_STREAM_NAME=<name>` – genau der Stream-Name, der auf dem Scout in go2rtc angelegt ist (z.B. `pc`, `cam`, `camera`).
3. Test: `python src/scripts/test_go2rtc_snapshot.py` – sollte ein Snapshot vom Scout-Stream liefern.

Damit nutzt ATLAS den gleichen `go2rtc_client` und dieselbe Snapshot-API, nur gegen die Scout-Instanz. Kein weiterer Code nötig.

---

## Logitech Brio (MX / 4K) unter Windows einbinden

Diese Anleitung beschreibt, wie eine Logitech Brio Kamera in `go2rtc` **auf dem PC** unter Windows eingebunden wird.

## Voraussetzungen

- **FFmpeg:** Die Skripte (Brio Snapshot-Server, Tapo RTSP/MP4) nutzen **zuerst** `driver/go2rtc_win64/ffmpeg.exe` und setzen das Arbeitsverzeichnis auf diesen Ordner (damit DLLs zuverlässig gefunden werden). So entstehen keine Konflikte mit anderem FFmpeg im PATH. Optional: System-FFmpeg (z.B. `winget install Gyan.FFmpeg`) und in .env `FFMPEG_PATH` setzen.
- **go2rtc**: Die `go2rtc.exe` befindet sich im gleichen Verzeichnis wie FFmpeg.

## Schritt 1 – Kameraname ermitteln

Um den exakten Namen der Kamera für FFmpeg zu finden, führe folgenden Befehl aus:

```powershell
& "C:\ATLAS_CORE\driver\go2rtc_win64\ffmpeg.exe" -list_devices true -f dshow -i dummy
```

Suche unter der Sektion „DirectShow video devices“ nach dem Namen deiner Kamera (z. B. `"Logitech BRIO"` oder `"Logitech BRIO 4K"`). Notiere dir diesen Namen exakt.

Alternativ kannst du die Datei `list_dshow_cameras.bat` im `driver/go2rtc_win64/`-Ordner ausführen.

## Schritt 2 – Stream anlegen

### Über die Web-UI
1. Öffne die go2rtc Web-UI unter [http://localhost:1984](http://localhost:1984).
2. Klicke auf **Streams** und dann auf **Add stream**.
3. **Name**: z. B. `pc`
4. **Source**:
   ```text
   exec:ffmpeg -f dshow -video_size 1920x1080 -framerate 30 -i video="Logitech BRIO" -c:v libx264 -preset ultrafast -f mpegts -
   ```
   *(Ersetze `"Logitech BRIO"` durch deinen notierten Namen)*

### Über die Config-Datei (go2rtc.yaml)
Erstelle eine `go2rtc.yaml` im Ordner `driver/go2rtc_win64/` mit folgendem Inhalt:

```yaml
streams:
  pc: exec:ffmpeg -f dshow -video_size 1920x1080 -framerate 30 -i video="Logitech BRIO" -c:v libx264 -preset ultrafast -f mpegts -
```

## Schritt 3 – Auflösung anpassen (Optional)

Für 4K Auflösung ändere den Parameter `-video_size`:
- **4K**: `-video_size 3840x2160`
- **Full HD**: `-video_size 1920x1080`

## Schritt 4 – Funktionstest

Führe das Test-Script aus, um zu prüfen, ob ein Snapshot erstellt werden kann:

```powershell
python src/scripts/test_go2rtc_snapshot.py
```

---

## On-Demand-Snapshot für die Brio (PC)

Wenn die Brio **nur bei Bedarf** ein Bild liefern soll (kein Dauerstream, LED nur beim Abruf an), kannst du den **On-Demand-Snapshot-Server** nutzen:

- **Skript:** `src/scripts/camera_snapshot_server.py` (startet einen kleinen HTTP-Server; bei jedem GET auf `/snapshot.jpg` wird einmal FFmpeg ausgeführt, ein Einzelbild von der Brio gelesen und zurückgegeben).
- **Voraussetzung:** FFmpeg aus `driver/go2rtc_win64/` (Skript setzt cwd dort); Kameraname in .env `CAMERA_DEVICE_NAME` (z.B. `Logitech BRIO`).
- **.env:** Optional `CAMERA_SNAPSHOT_URL=http://localhost:8555/snapshot.jpg` setzen. Der `go2rtc_client` nutzt dann diese URL für MX-Abfragen (Snapshot = On-Demand-Aktivierung der Webcam).
- **Stabiler Ablauf:** Für MX-Tests oder Brio-Szenario den **Snapshot-Server vorher starten** (in einem eigenen Terminal: `python src/scripts/camera_snapshot_server.py`), danach z.B. `python src/scripts/mx_save_images_only.py` oder `brio_scenario_periodic.py`. Alternativ go2rtc mit Brio-Stream laufen lassen und `CAMERA_SNAPSHOT_URL` leer lassen (dann wird go2rtc genutzt).

So bleibt die Webcam im Alltag aus und wird nur bei einem Aufruf kurz aktiviert.

---

## Tapo (Balkon): Erkennungstest in den Garten

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

## Brio-Szenario: periodische Auswertung (Person + Zustand, Protokoll)

Damit ATLAS **zur Laufzeit** erkennen kann, ob etwas nicht stimmt (Anwesenheit, Auffälligkeiten), muss **mindestens einmal pro Minute** ein Bild ausgewertet werden – ein Intervall von 50 Minuten wäre für solche Zwecke wertlos (z.B. Erkennung von Notfällen). Für den ersten Test kannst du das Intervall per .env auf 50 min stellen; für den eigentlichen Betrieb ist **1× pro Minute** der sinnvolle Standard.

- **Skript:** `python src/scripts/brio_scenario_periodic.py`  
  - **Standard:** alle **1 Minute** ein Zyklus, **60 Minuten** lang (also 60 Zyklen).  
  - Ein Zyklus: 1 Snapshot → Gemini Vision (Person ja/nein, STATE, NEED_MORE) → bei NEED_MORE bis zu 5 weitere Snapshots → erneute Auswertung → Eintrag ins Protokoll.
- **Einmaliger Test:** `python src/scripts/brio_scenario_periodic.py once`
- **Protokoll:** `data/brio_scenario/protocol.jsonl` (eine Zeile pro Zyklus, JSON mit `ts`, `person_visible`, `state`, `images_used`, `image_paths`).
- **Bilder** werden unter `data/brio_scenario/` abgelegt (`brio_*.jpg`, ggf. `brio_extra_*.jpg`).
- **.env (optional):** `BRIO_SCENARIO_INTERVAL_MIN=1` (Standard: 1 min; für ersten Test z.B. `50`), `BRIO_SCENARIO_DURATION_MIN=60`, `BRIO_SCENARIO_MAX_EXTRA=5`, `BRIO_SCENARIO_LOG_DIR`, `BRIO_VISION_MODEL=gemini-3.1-pro-preview`. Kamera wie gewohnt (GO2RTC_* oder CAMERA_SNAPSHOT_URL); für Vision wird `GEMINI_API_KEY` benötigt.

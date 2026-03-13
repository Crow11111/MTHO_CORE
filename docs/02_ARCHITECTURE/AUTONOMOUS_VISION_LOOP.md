<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# MISSION: DAS ALLSEHENDE AUGE (AUTONOMOUS VISION LOOP)

**Status:** DRAFT
**Verantwortlich:** System Architect
**Datum:** 2026-03-05

## 1. Mission Statement

CORE soll die passive Rolle verlassen. Statt auf "Was siehst du?" zu warten, soll das System **proaktiv** sehen.
Der `atlas_vision_daemon` ist ein autonomer Hintergrundprozess, der den visuellen Kortex des Systems darstellt. Er beobachtet kontinuierlich, filtert Irrelevantes (Stille) und eskaliert Relevantes (Bewegung) an das Bewusstsein (Gemini/Zero-State).

*Grundsatz: Das System beobachtet, um zu verstehen, nicht um zu speichern (Überwachung vs. Wahrnehmung).*

---

## 2. Architektur

Der Prozess läuft lokal auf dem Core-Server (4D_RESONATOR (CORE)) oder einem dedizierten Vision-Node (Scout/Jetson).

```mermaid
graph TD
    CAM[Kamera (MX Brio)] -->|RTSP Stream| GO2RTC[go2rtc Server]
    GO2RTC -->|RTSP/MJPEG| DAEMON[atlas_vision_daemon.py]
    
    subgraph "Lokal: Vision Loop (10-30 FPS)"
        DAEMON -->|cv2.VideoCapture| FRAME[Frame Grabber]
        FRAME -->|Grayscale/Blur| PREPROC[Preprocessing]
        PREPROC -->|Frame Diff / MOG2| MOTION[Motion Detector]
        MOTION -->|Delta > Threshold?| TRIGGER{Bewegung?}
    end
    
    TRIGGER -->|Nein| SLEEP[Wait / Loop]
    TRIGGER -->|Ja + Cooldown abgelaufen| SNAPSHOT[Snapshot ziehen]
    
    subgraph "Cloud: Kognition"
        SNAPSHOT -->|API Call| GEMINI[Gemini 1.5 Flash/Pro Vision]
        GEMINI -->|"Beschreibe Ereignis"| DESC[Text-Beschreibung]
    end
    
    subgraph "Memory: Zero-State Feld"
        DESC -->|Ingest| CHROMA[ChromaDB: zero_state_field]
        CHROMA -->|Context| ORCHESTRATOR[Orchestrator / Brain]
    end
```

---

## 3. Komponenten & Datenfluss

### 3.1. Input: Der Stream
- **Quelle:** `go2rtc` (lokal oder auf Scout).
- **Protokoll:** RTSP (bevorzugt für OpenCV) oder MJPEG (Fallback).
- **URL:** `rtsp://127.0.0.1:8554/mx_brio` (oder via `src/network/go2rtc_client.py` Config).

### 3.2. Der Daemon (`src/daemons/atlas_vision_daemon.py`)
Ein Python-Skript, das als System-Service läuft.

**Logik:**
1.  **Verbindung:** Öffnet RTSP-Stream via `cv2.VideoCapture`.
2.  **Schleife:** Liest Frames.
3.  **Motion Detection (Low-Cost):**
    *   Vergleich aktueller Frame vs. Referenz-Frame (laufender Durchschnitt oder letzter Keyframe).
    *   Berechnung der "Motion Energy" (Anzahl geänderter Pixel).
    *   Wenn `Motion Energy > THRESHOLD`: **EVENT TRIGGER**.
4.  **Cooldown:** Nach einem Event wird für `X` Sekunden (z.B. 10s) keine neue Analyse gestartet, um Spam zu vermeiden.
5.  **Kognition:**
    *   Sendet den *aktuellen Frame* (im Speicher) an Gemini Vision API.
    *   Prompt: *"Beschreibe prägnant (1 Satz), was gerade passiert. Fokus auf Personen, Handlungen oder Zustandsänderungen. Ignoriere Rauschen."*
6.  **Gedächtnis:**
    *   Speichert das Ergebnis in ChromaDB (`zero_state_field`).
    *   Metadaten: `source=vision_daemon`, `type=observation`, `timestamp=ISO`.

### 3.3. Schnittstellen

#### A. Google Gemini API (Direkt)
Um Latenz und Abhängigkeiten zu minimieren, nutzt der Daemon das `google-generativeai` SDK direkt (statt via OpenClaw VPS), sofern ein lokaler API-Key vorhanden ist.
*Fallback:* OpenClaw Brain API.

#### B. ChromaDB (Zero-State)
Nutzung von `src/network/chroma_client.py`.
- **Funktion:** `add_event_to_chroma` oder spezifisch `add_zero_state_observation`.
- **Ziel-Collection:** `zero_state_field` (Das Kurzzeitgedächtnis für Wahrnehmungen).

---

## 4. Implementierungs-Details (Spezifikation)

### 4.1. Konfiguration (`.env`)
```bash
VISION_DAEMON_ENABLED=true
VISION_RTSP_URL=rtsp://localhost:8554/mx_brio
VISION_MOTION_THRESHOLD=5000  # Pixel-Anzahl
VISION_COOLDOWN_SECONDS=15
VISION_MODEL=gemini-1.5-flash  # Schnell & Kosteneffizient
```

### 4.2. Python Requirements
- `opencv-python` (headless empfohlen für Server)
- `google-generativeai`
- `chromadb`
- `numpy`

### 4.3. Zero-State-Integration
Jedes Vision-Event wird ein "Fakt" im Zero-State-Feld.
Beispiel-Eintrag:
```json
{
  "document": "Eine Person (Marc) hat den Raum betreten und setzt sich an den Schreibtisch.",
  "metadata": {
    "source": "vision_daemon",
    "type": "observation",
    "confidence": "high",
    "timestamp": "2026-03-05T14:30:00"
  }
}
```

---

## 5. Nächste Schritte

1.  [ ] `src/daemons/atlas_vision_daemon.py` implementieren.
2.  [ ] `src/network/chroma_client.py` erweitern um `add_zero_state_observation`.
3.  [ ] Testlauf mit `gemini-1.5-flash` (Latenz-Check).
4.  [ ] Integration in den Autostart (PM2 oder Systemd).

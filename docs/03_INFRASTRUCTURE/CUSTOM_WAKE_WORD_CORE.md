<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

﻿# Custom Wake Word: CORE

Anleitung zum Erstellen eines Custom Wake Words "CORE" fuer openWakeWord in Home Assistant.

---

## 1. Aktueller Stand

| Eigenschaft | Wert |
|-------------|------|
| **Wake Word Entity** | `wake_word.openwakeword` |
| **Pipeline** | CORE (ID: `01hzktez4kncsm0sr1qx32hy5x`) |
| **Aktuelles Wake Word** | `hey_jarvis_v0.1` |
| **openWakeWord Host** | `core-openwakeword:10400` |

---

## 2. Verfuegbare Standard Wake Word Models

openWakeWord bietet folgende **vorgefertigte Models** an:

| Model | Beschreibung | Verfuegbarkeit |
|-------|--------------|----------------|
| `ok_nabu` | "Ok Nabu" - Home Assistant default | Standard |
| `hey_nabu` | "Hey Nabu" | Standard |
| `hey_jarvis_v0.1` | "Hey Jarvis" (Star Trek/Iron Man Style) | **Aktuell aktiv** |
| `hey_mycroft` | "Hey Mycroft" (Mycroft AI) | Standard |
| `alexa` | "Alexa" (Amazon Style) | Standard |
| `hey_rhasspy` | "Hey Rhasspy" | Standard |

### Community Wake Word Models

Von [fwartner/home-assistant-wakewords-collection](https://github.com/fwartner/home-assistant-wakewords-collection):

| Model | Beschreibung | Accuracy | Download |
|-------|--------------|----------|----------|
| `computer_v2` | "Computer" / "Hey Computer" (Star Trek LCARS) | 78.3% | [Link](https://github.com/fwartner/home-assistant-wakewords-collection/tree/main/en/computer) |
| `hal` | "HAL" (2001 Space Odyssey) | - | [Link](https://github.com/fwartner/home-assistant-wakewords-collection/tree/main/en/hal) |
| `hey_jarvis` | "Hey Jarvis" | - | Community |
| `glados` | "GLaDOS" (Portal) | - | Community |

---

## 3. "Computer" Wake Word JETZT aktivieren

Das `computer_v2.tflite` Model wurde bereits heruntergeladen und auf Scout kopiert.

**Speicherort auf Scout:** `/share/openwakeword/computer_v2.tflite`

### 3.1 openWakeWord Add-on konfigurieren

1. **HA Web-UI oeffnen:** https://192.168.178.54:8123
2. **Navigation:** Einstellungen > Add-ons > openWakeWord > Konfiguration
3. **Custom Model Pfad hinzufuegen:**
   `yaml
   custom_model_dir: /share/openwakeword
   `
4. **Add-on neustarten**

### 3.2 Pipeline Wake Word aendern

Nach Add-on Neustart erscheint `computer_v2` in der Wake Word Auswahl:

1. **Navigation:** Einstellungen > Voice assistants > CORE > Wake word
2. **Auswahl:** `computer_v2` aus der Liste waehlen
3. **Speichern**

### 3.3 Alternativ: Direkt in Storage-Datei

Editiere `S:\.storage\assist_pipeline.pipelines`:

`json
{
  "wake_word_entity": "wake_word.openwakeword",
  "wake_word_id": "computer_v2"
}
`

Nach Aenderung HA neustarten.

---

## 4. Custom Wake Word "CORE" trainieren

### 4.1 Voraussetzungen

- Python 3.9+ mit pip
- Audio-Aufnahmen des Wake Words (min. 50-100 Samples empfohlen)
- Negativ-Samples (Sprache ohne Wake Word)

### 4.2 openWakeWord Training Repository

`bash
git clone https://github.com/dscripka/openWakeWord
cd openWakeWord
pip install -e .[training]
`

### 4.3 Daten-Struktur erstellen

`
training_data/
+-- positive/
|   +-- atlas_001.wav
|   +-- atlas_002.wav
|   +-- ... (min. 50 Aufnahmen von "CORE")
+-- negative/
    +-- random_speech_001.wav
    +-- ... (Hintergrund/andere Sprache)
`

**Audio-Anforderungen:**
- Format: WAV, 16kHz, Mono, 16-bit
- Laenge: 1-3 Sekunden pro Sample
- Verschiedene Sprecher und Umgebungen empfohlen

### 4.4 Training durchfuehren

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

### 4.5 Model deployen

`bash
# Model nach Scout kopieren
copy models\core\atlas_v1.tflite S:\share\openwakeword\
`

---

## 5. Installierte Models (lokal)

| Datei | Groesse | Beschreibung |
|-------|---------|--------------|
| `hey_jarvis_v0.1.tflite` | 1.2 MB | Standard Jarvis Model |
| `computer_v2.tflite` | 207 KB | Star Trek "Computer" |

Speicherort auf 4D_RESONATOR (CORE): `c:\CORE\data\openwakeword_models\`
Speicherort auf Scout: `/share/openwakeword/`

---

## 6. Naechste Schritte

| Schritt | Beschreibung | Status |
|---------|--------------|--------|
| 1 | "computer" Model auf Scout kopiert | ERLEDIGT |
| 2 | openWakeWord Custom Model Pfad konfigurieren | **MANUELL** |
| 3 | Pipeline auf "computer_v2" umstellen | **MANUELL** |
| 4 | CORE Wake Word Samples aufnehmen | Ausstehend |
| 5 | CORE Custom Training durchfuehren | Ausstehend |

---

## 7. Referenzen

- [openWakeWord GitHub](https://github.com/dscripka/openWakeWord)
- [Home Assistant Wake Words](https://www.home-assistant.io/voice_control/create_wake_word/)
- [Community Wake Word Collection](https://github.com/fwartner/home-assistant-wakewords-collection)
- [Wyoming Protocol](https://github.com/rhasspy/wyoming)
- [LCARS Star Trek Computer](https://en.wikipedia.org/wiki/LCARS)

---

*Erstellt: 2026-03-04*
*Pipeline: CORE (01hzktez4kncsm0sr1qx32hy5x)*

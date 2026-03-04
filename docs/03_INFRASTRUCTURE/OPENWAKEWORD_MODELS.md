# openWakeWord – Verfügbare Modelle

**Zweck:** Übersicht der vordefinierten und Custom Wake Word Modelle für ATLAS/Scout.

**Quelle:** [openWakeWord GitHub](https://github.com/dscripka/openWakeWord), [Hugging Face](https://huggingface.co/davidscripka/openwakeword)

---

## 1. Vordefinierte Modelle (openWakeWord v0.5.1 / v0.6.0)

| Modell-ID      | Wake Word      | Beschreibung                    | Ähnlich zu |
|----------------|----------------|----------------------------------|------------|
| `alexa`        | alexa          | Ein-Wort-Trigger                 | –          |
| `hey_mycroft`  | hey mycroft    | Zwei-Wort-Phrase                | hey atlas  |
| `hey_jarvis`   | hey jarvis     | Zwei-Wort-Phrase (Computer-Assistent) | computer, hey atlas |
| `hey_rhasspy`  | hey rhasspy    | Zwei-Wort-Phrase                | hey atlas  |
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

## 2. „Computer“ und „Atlas“

### 2.1 „Computer“

| Frage                         | Antwort |
|------------------------------|---------|
| Gibt es „computer“ vordefiniert? | **Nein** |
| Ähnliche Modelle              | `hey_jarvis` (Computer-Assistent-Kontext) |
| Lösung                        | Custom Training (siehe [Custom Wake Word Training](#3-custom-wake-word-training)) |

### 2.2 „Atlas“ / „hey atlas“

| Frage                         | Antwort |
|------------------------------|---------|
| Gibt es „atlas“ vordefiniert? | **Nein** |
| Ähnliche Modelle              | `hey_mycroft`, `hey_jarvis`, `hey_rhasspy` (alle Zwei-Wort-Phrasen) |
| Lösung                        | Custom Training (siehe [Custom Wake Word Training](#3-custom-wake-word-training)) |

---

## 3. Home Assistant Add-on: „ok nabu“

Das **ok nabu** Wake Word wird von Home Assistant empfohlen und ist im openWakeWord Add-on bzw. der Wyoming-Integration verfügbar. Es stammt aus dem HA Voice-Projekt und ist **nicht** Teil der offiziellen openWakeWord-Modellliste – wird aber vom HA Add-on bereitgestellt.

**Verwendung:** Zum Testen der Wake-Word-Pipeline vor dem Training eigener Modelle.

---

## 4. Lizenz

Alle vordefinierten Modelle: **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International** (CC BY-NC-SA 4.0) – wegen Datensätzen mit restriktiver Lizenz im Training.

---

## 5. Referenzen

| Thema              | URL |
|--------------------|-----|
| openWakeWord       | https://github.com/dscripka/openWakeWord |
| Hugging Face       | https://huggingface.co/davidscripka/openwakeword |
| Wyoming-openWakeWord | https://github.com/rhasspy/wyoming-openwakeword |
| HA Wake Words      | https://www.home-assistant.io/voice_control/create_wake_word/ |

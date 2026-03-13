<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Voice Pipeline – Audio-Input Durchstich

**Problem:** Pipeline konfiguriert (Whisper, Piper, openWakeWord, CORE Conversation), aber **kein Audio-INPUT** erreicht die Assist Pipeline. Brio-Audio ist in go2rtc sichtbar, aber go2rtc liefert nicht an Assist.

---

## 1. Architektur-Entscheidung

### Kernbefund

| Komponente | Funktion | Audio-Rolle |
|------------|----------|-------------|
| **go2rtc** | RTSP/WebRTC-Stream (Video+Audio) | Konsumiert Brio-Mikro via PulseAudio. **Liefert NICHT an Assist.** |
| **Assist Pipeline** | Wake Word → STT → Agent → TTS | Erwartet Audio von **Wyoming Satellite** (Client-Push). |
| **Assist Microphone Add-on** | Wyoming Satellite auf HA OS | Liest von Host-Mikrofon (PulseAudio/ALSA), streamt an Wyoming. |

**go2rtc und Assist teilen sich keine Pipeline.** go2rtc ist ein Stream-Server; Assist braucht einen **Audio-Client** (Satellite), der PCM an Wyoming sendet.

### Entscheidung: Weg 1 (produktionsreif)

**Assist Microphone Add-on** installieren und starten. Es nutzt dieselbe Hardware (Brio USB) wie go2rtc – beide lesen von PulseAudio. Kein go2rtc-Umbau nötig.

---

## 2. Implementierungsschritte

### 2.1 Assist Microphone Add-on prüfen/installieren

**Prüfung (SSH auf Scout oder HA Supervisor API):**

```bash
# Via HA Supervisor API (von 4D_RESONATOR (CORE), mit HASS_TOKEN):
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

### 2.2 Assist Microphone mit Pipeline verbinden

1. **Einstellungen → Sprachassistenten**
2. Assistent „CORE“ bearbeiten
3. **Streaming Wake Word** prüfen: openWakeWord + Modell (z.B. „Computer“)
4. **Voice Satellite:** Assist Microphone muss als verbundenes Gerät erscheinen

Falls kein Satellite sichtbar:

- Assist Microphone Add-on neu starten
- HA neu starten
- **Einstellungen → Geräte & Dienste → Wyoming** prüfen – neues Gerät sollte erscheinen

### 2.3 Audio-Quelle (Brio vs. Headset)

Laut `SCOUT_GO2RTC_CONFIG.md`:

- **Brio:** `alsa_input.usb-046d_Logitech_BRIO_657ACFE9-03.analog-stereo`
- **Headset:** `alsa_input.usb-Samsung_USBC_Headset_20190816-00.mono-fallback`

Assist Microphone nutzt typisch das **Standard-Eingabegerät**. Auf dem Scout:

1. **Einstellungen → System → Hardware** – prüfen, welches Mikro als Standard gesetzt ist
2. Falls Brio gewünscht: In PulseAudio/ALSA das Brio-Mikro als Default setzen (HA OS: ggf. über Add-on-Konfiguration, falls vorhanden)

**Falls nur Brio angeschlossen:** Sollte automatisch als einziges Mikro genutzt werden.

### 2.4 Konfiguration Assist Microphone (optional)

In **Add-on → Konfiguration** (falls verfügbar):

```yaml
# Beispiel – exakte Keys je nach Add-on-Version prüfen
mic_volume: 1.0
auto_gain: true
noise_suppression: 1
```

---

## 3. Verifikation

### 3.1 Satellite-Status

```bash
python check_assist_satellite.py
```

Erwartung: Entities mit `assist`, `satellite`, `microphone`; Wyoming-Devices mit Assist Microphone.

### 3.2 Voice-Integration-Test

```bash
python -m src.scripts.test_ha_voice_integration
```

### 3.3 Manueller Pipeline-Test

1. Wake Word sagen (z.B. „Computer“)
2. Befehl sprechen (z.B. „Licht an“)
3. Erwartung: Whisper transkribiert → CORE Conversation → Piper spricht Antwort

---

## 4. Fallback-Optionen

### Fallback A: Assist Microphone nicht verfügbar / funktioniert nicht

**Wyoming Satellite Add-on** (falls als separates Add-on im Store):

- Äquivalent zu Assist Microphone, evtl. anderer Hersteller (z.B. Rhasspy)
- Installation analog, dann mit Pipeline verbinden

### Fallback B: RTSP → Wyoming Bridge (Custom)

**Aufwand:** Hoch. **Nur wenn Weg 1 definitiv scheitert.**

1. Skript auf Scout (oder separatem Host): FFmpeg zieht RTSP-Audio von go2rtc
2. PCM-Stream (16 kHz, mono, S16_LE) an Wyoming-Client senden
3. Wyoming-Client-Implementierung erforderlich (z.B. `wyoming-satellite` als Library)

**Einschränkung:** HA OS = kein Root, Add-on-Container. Custom-Skript müsste als Add-on gepackt werden.

### Fallback C: 4D_RESONATOR (CORE) Voice Satellite (bereits vorhanden)

`src/voice/dreadnought_voice_satellite.py` – nutzt Mikro **am PC**, nicht am Scout.

- **Nicht** für Scout-Brio geeignet
- Nur wenn Voice-Input vom 4D_RESONATOR (CORE)-PC gewünscht ist

### Fallback D: ESP32/Atom Echo Hardware-Satellite

Physisches Gerät mit Mikro, verbindet sich per Wyoming mit HA. Ersetzt Software-Mikrofon am Scout.

---

## 5. Checkliste (Kurz)

| # | Aktion | Befehl / Ort |
|---|--------|--------------|
| 1 | Assist Microphone installiert? | Einstellungen → Add-ons |
| 2 | Assist Microphone gestartet? | Add-on-Detail → Start |
| 3 | Satellite in Pipeline sichtbar? | Einstellungen → Sprachassistenten |
| 4 | Brio als Mikro erkannt? | System → Hardware |
| 5 | Wake Word + Befehl testen | „Computer“ → „Licht an“ |

---

## 6. Referenzen

- `SCOUT_ASSIST_PIPELINE.md` – Pipeline-Architektur
- `SCOUT_GO2RTC_CONFIG.md` – Brio/Headset PulseAudio-Quellen
- `usb_microphone_research.md` – Assist Microphone als Audio-Input
- `install_assist_mic.py` – Installationsskript
- [HA Voice Control](https://www.home-assistant.io/voice_control/)
- [Wyoming Protocol](https://www.home-assistant.io/integrations/wyoming/)

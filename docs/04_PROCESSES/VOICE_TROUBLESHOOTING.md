<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Voice Assistant – Troubleshooting

---

## 1. Keine Antwort nach Wake Word

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| Kein Reaktion auf "Hey CORE" | openWakeWord nicht aktiv | HA: Einstellungen → Sprachassistenten → Wake Word prüfen |
| STT startet nicht | Whisper Add-on fehlt | Wyoming Add-ons installieren (Whisper, Piper, openWakeWord) |
| Text wird nicht an CORE gesendet | Conversation Agent falsch | CORE Conversation Integration als Agent wählen |
| 401/503 von CORE | HA_WEBHOOK_TOKEN fehlt | `.env`: HA_WEBHOOK_TOKEN setzen, in HA-Geheimnisse eintragen |

---

## 2. Befehl wird nicht erkannt

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| "Regal 80% Helligkeit" → Unbekannt | Entity "Regal" nicht in Index | `data/home_assistant/states.json` aktualisieren oder entities im Context übergeben |
| Parser liefert None | Kein Pattern-Match, LLM-Fallback aus | Ollama/Gemini für LLM-Fallback konfigurieren |
| Falsche Entity gewählt | Fuzzy-Match zu ähnlich | friendly_name in HA präzisieren |

---

## 3. HA-Service wird nicht ausgeführt

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| "Befehl ausgeführt" aber Licht reagiert nicht | entity_id falsch oder nicht vorhanden | HA: Entwicklerwerkzeuge → Zustände prüfen |
| HAClient Fehler | HASS_URL/HASS_TOKEN falsch | `.env` prüfen, Token in HA Profil erneuern |
| SSL-Fehler | Self-Signed Zertifikat | `verify=False` in HAClient (bereits gesetzt) |

---

## 4. TTS funktioniert nicht

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| Keine Sprachausgabe auf Mini | TTS_CONFIRMATION_ENTITY falsch | media_player Entity prüfen (z.B. media_player.schreibtisch) |
| ElevenLabs nicht genutzt | TTS_TARGET=mini (Default) | TTS_TARGET=elevenlabs_stream für ElevenLabs auf Mini |
| Piper Fallback fehlgeschlagen | PIPER_VOICE_PATH nicht gesetzt | `python -m piper.download_voices de_DE-lessac-medium` |
| Stream zu Mini fehlgeschlagen | Mini erreicht CORE_HOST_IP nicht | CORE_HOST_IP auf erreichbare IP setzen, Firewall prüfen |

---

## 5. NASA Sound spielt nicht

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| Datei nicht gefunden | nasa_mission_complete.mp3 fehlt | `python -m src.scripts.download_nasa_sound` |
| play_media fehlgeschlagen | HASS_URL/TOKEN fehlt | `.env` prüfen |
| Mini streamt nicht | Port 8002 blockiert / falsche IP | CORE_HOST_IP, TTS_STREAM_PORT prüfen |

---

## 8. Bekannte Bugfixes

| Bug | Ursache | Fix | Datum |
|-----|---------|-----|-------|
| TTS Night-Agent Bug – Sprachausgabe bleibt stumm trotz korrektem Flow | `dispatch_tts()` wurde ohne `await` aufgerufen, asyncer Aufruf lief nicht durch | `await dispatch_tts(...)` in `scout_direct_handler.py` | 2026-03-05 |
| stop_gc_loop Crash – Event-Bus stuerzt nach GC-Zyklus ab | `stop_gc_loop()` wurde auf nicht-gestarteten GC-Loop aufgerufen | Guard-Check `if self._gc_task:` vor `stop_gc_loop()` in `core_agent.py` | 2026-03-05 |

---

## 6. Test-Skripte

```bash
# E2E Voice Test (Parser + optional HA + NASA Sound)
python -m src.scripts.test_voice_e2e

# Wyoming-Integration prüfen (STT, TTS, Wake Word)
python -m src.scripts.test_ha_voice_integration

# ElevenLabs TTS testen
python -m src.scripts.test_elevenlabs_output
```

---

## 7. Logs

- **CORE API:** `loguru` – LOG_LEVEL in `.env`
- **HA:** Einstellungen → System → Logs
- **Wyoming:** Add-on-Logs in HA

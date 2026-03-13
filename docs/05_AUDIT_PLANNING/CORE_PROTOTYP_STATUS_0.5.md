<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Prototyp-Status 0.6

**Stand:** 28.02.2026 | **Phase:** Erste Schnittstellen funktionsfähig (Prototyp 0.6)

---

## Was läuft

| Komponente | Status | Beweis |
|------------|--------|--------|
| OpenClaw Admin (OMEGA_ATTRACTOR) | LÄUFT | Z1–Z5; API 18789, Nginx 443 |
| Scout → OMEGA_ATTRACTOR (Event) | LÄUFT | send_event_to_oc_brain, scout_send_event_to_oc |
| Event-Ingest | LÄUFT | POST /api/core/event, GET /api/core/events, data/events |
| Voice (ElevenLabs) | LÄUFT | POST /api/core/tts, GET /api/core/voice/roles |
| OMEGA_ATTRACTOR im Task-Loop | LÄUFT | send_message_to_agent; Priorisierung getestet |
| API-Health gebündelt | LÄUFT | GET /api/core/status (Gateway, Event-Ingest, Voice-Roles, letzte Event-IDs) |
| Spine ↔ Brain (Config) | LÄUFT | gateway.remote in deploy_vps_full_stack.py |
| E2E Event→OC→TTS | LÄUFT | e2e_event_to_tts.py (Z13) |
| Voice-IDs (alle Rollen) | LÄUFT | voice_config: Fallback atlas_dialog (Z11) |
| Scout HA Doku | LÄUFT | Z9: SCOUT_HA_EVENT_AN_OC_BRAIN.md Copy-Paste bereit |
| fetch_oc_submissions Roundtrip | LÄUFT | Z15: OC schreibt, 4D_RESONATOR (CORE) holt |

---

## Offen

| Priorität | Ziel |
|-----------|------|
| User-Aktion | YAML aus Doku in HA einfügen (Scout live). |
| Nächste | Hören, Sehen, Scout live. |

---

## Nächste Prioritäten

- Hören: Pipeline Scout-Mikro/Assist → CORE.
- Sehen: go2rtc oder CAMERA_SNAPSHOT_URL lauffähig.
- Scout live: User fügt Doku (SCOUT_HA_EVENT_AN_OC_BRAIN.md) in HA ein.

---

## Test an 4D_RESONATOR (CORE)

```bash
python -m src.scripts.test_dreadnought_pipeline
python -m src.scripts.e2e_event_to_tts --type e2e_test --node dreadnought
```

API auf Port 8000 starten für volle Prüfung (Voice/roles, Event-Ingest).

---

## Sensorik / Signal-I/O (Scout)

- **Sehen/Hören:** Kamera + Mikro per USB am Raspi 5 (HA OS) – siehe `SCOUT_USB_KAMERA_MIKRO_HA_OS.md`. Nach Neustart: USB prüfen, FFmpeg/MotionEye für Kamera, ggf. Assist für Mikro.
- **Scout → OMEGA_ATTRACTOR:** Event nach Neustart oder bei Trigger – `SCOUT_HA_EVENT_AN_OC_BRAIN.md` (rest_command + Automation).
- **CORE Sprechen:** `python -m src.scripts.test_atlas_speak` – TTS (ElevenLabs) und/oder WhatsApp via HA. TTS getestet (OK); WhatsApp sobald Scout/HA wieder erreichbar.

---

## Referenz

- Zwischenziele: `ATLAS_ZWISCHENZIELE.md`
- Schnittstellen: `docs/02_ARCHITECTURE/ATLAS_SCHNITTSTELLEN_UND_KANAALE.md`
- Architektur: `docs/02_ARCHITECTURE/ATLAS_NEOCORTEX_V1.md`

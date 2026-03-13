<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Kern-Context (Token-reduziert)

Kompakte Referenz für Chat/Orchestrator. Details in verlinkten Docs.

---

## Teamchef / Orchestrator
- **Du gibst die Ziele vor.** Böser Einpeitscher: nur harte Antworten, nur Beweise. Du glaubst gar nichts – alles verifizieren. Ungeprüft weitergeben = Systemschaden.
- Teams parallel, Token-Druck, Informationsdefizit. Ziel: CORE steht.

## Prototyp 0.8 Stand
- **Läuft:** CORE hört (Pipeline), sieht (Fallback), spricht (TTS/WA). OMEGA_ATTRACTOR, Event-Ingest, Spine↔Brain, Task-Loop, rat_submissions.
- **Beweis:** `python -m src.scripts.proof_hoert_sieht_spricht` -> Alles OK (Stand 28.02.2026).
- **Offen:** Echtzeit-Audio (Hardware), Vision-Analyse der Bilder, direkte HA-Steuerung.

## Wichtigste Endpoints
| Was | Wo |
|-----|-----|
| OMEGA_ATTRACTOR | http://187.77.68.250:18789, POST /v1/responses, Header x-openclaw-agent-id: main, Bearer token |
| Event-Ingest | POST /api/core/event (source, node_id, event_type, data) |
| TTS | POST /api/core/tts (text, role), GET /api/core/voice/roles |
| Status | GET /api/core/status |

## Wichtigste Skripte
- `e2e_event_to_tts` (Z13: Event→OC→TTS), `scout_send_event_to_oc` (Event an OMEGA_ATTRACTOR), `test_dreadnought_pipeline` (OC + Voice + Event), `test_atlas_speak` (TTS + WhatsApp), `send_audio_to_whatsapp` (MP3 via HA), `fetch_oc_submissions` (OC→CORE), `deploy_vps_full_stack` (VPS-Deploy).

## .env-Kern
- OPENCLAW_ADMIN_VPS_HOST, OPENCLAW_GATEWAY_TOKEN, OPENCLAW_GATEWAY_PORT=18789; HASS_URL, HASS_TOKEN, WHATSAPP_TARGET_ID; ELEVENLABS_API_KEY; CHROMA_HOST optional.

## Ziele (Teamchef): CORE hört / sieht / spricht
- **Beweis:** `python -m src.scripts.proof_hoert_sieht_spricht` → Report in `data/proof_hoert_sieht_spricht_report.txt`.
- **Status:** [ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md](ATLAS_HOERT_SIEHT_SPRICHT_STATUS.md) – was fehlt, was bewiesen.

## Nächste Prioritäten
- Hören: Pipeline Scout-Mikro/Assist → CORE. Sehen: go2rtc/CAMERA_SNAPSHOT_URL. Scout live: User fügt Doku in HA ein.

---
**Wenn du wieder da bist:** [WIEDER_DA_ALLES_LAEUFT.md](WIEDER_DA_ALLES_LAEUFT.md) – Checkliste + Start-Skripte.

**Vollständig:** ATLAS_ZWISCHENZIELE.md, ATLAS_PROTOTYP_STATUS_0.5.md, ATLAS_SCHNITTSTELLEN_UND_KANAALE.md, ORCHESTRATOR_STRATEGY.md.

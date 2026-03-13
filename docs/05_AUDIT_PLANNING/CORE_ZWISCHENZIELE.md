<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# CORE Zwischenziele (Orchestrator-vorgegeben)

**Verantwortung:** Orchestrator setzt Ziele, setzt Teams an, verifiziert jeden Beweis selbst.  
**Phase:** Prototyp 0.5–0.6 – erste Schnittstellen funktionsfähig. TEAM baut CORE; OMEGA_ATTRACTOR einbeziehen (Teilaufgaben, Orchestrierung, Anfragen).

---

## Offene Ziele (Prototyp 0.5–0.6)

| Z  | Ziel | Beweiskriterium |
|----|------|------------------|
| **Z7** | OC Spine an Brain angebunden | Spine-Config auf VPS: Brain als Remote/Gateway. Orchestrator prüft Config/Logs. |
| **Z9** | Scout-MX (USB) in HA aktiv | MX Brio an Scout liefert Bild an HA (`camera.scout_mx`). `proof_MX_HA.py` zeigt Erfolg. |
| **Z11** | Voice: Leere voice_id in voice_config belegen | Rollen mit voice_id="" erhalten gültige ElevenLabs-Voice-IDs oder Fallback. Team/OMEGA_ATTRACTOR: Vorschläge. |
| **Z12** | OMEGA_ATTRACTOR in Task-Loop | Konkrete Teilaufgabe an OMEGA_ATTRACTOR senden (z. B. "Priorisiere nächste 3 CORE-Zwischenziele"); Antwort strukturiert nutzbar. |
| **Z13** | E2E: Event → OMEGA_ATTRACTOR → Antwort → optional TTS | Ein Event löst OC-Antwort aus; Antwort kann an /api/core/tts übergeben werden. Verifikation durch Orchestrator. |
| **Z14** | API-Health + OC-Status gebündelt | Ein Endpoint oder Skript liefert Status: Gateway, Event-Ingest, Voice-Roles, letzte Events. Für 4D_RESONATOR (CORE)-Dashboard. |
| **Z15** | rat_submissions Roundtrip | OMEGA_ATTRACTOR schreibt in rat_submissions; 4D_RESONATOR (CORE) holt per fetch; Inhalt verifiziert. |
| **Z16** | Dokumentation: Prototyp-Status 0.5 | Eine Seite: was läuft, was offen, nächste 5 Ziele. Referenz für alle Teams. |

---

## Abgeschlossen

| Z  | Status | Beweis (Orchestrator) |
|----|--------|------------------------|
| Z1–Z5 | LÄUFT | 28.02.2026 OpenClaw Admin |
| **Z6** | **LÄUFT** | send_event_to_oc_brain → OMEGA_ATTRACTOR antwortet. |
| **Z7** | **LÄUFT** | deploy_vps_full_stack setzt gateway.remote (url openclaw-admin:18789, token) für Spine. |
| **Z8** | **LÄUFT** | POST/GET /api/core/event, data/events; ChromaDB optional. |
| **Z10** | **LÄUFT** | POST /api/core/tts, GET /api/core/voice/roles. |
| **Z12** | **LÄUFT** | OMEGA_ATTRACTOR Teilaufgabe (Priorisierung) gesendet, strukturierte Antwort. |
| **Z14** | **LÄUFT** | GET /api/core/status (Gateway, event_ingest_present, voice_roles_count, last_3_event_ids). |
| **Z16** | **LÄUFT** | ATLAS_PROTOTYP_STATUS_0.5.md angelegt. |

---

## Test an 4D_RESONATOR (CORE)

`python -m src.scripts.test_dreadnought_pipeline` – prüft OMEGA_ATTRACTOR, Voice/roles, Event-Ingest (letztere zwei nur wenn API auf 8000 läuft).

---

## Nächste Aktionen (Orchestrator, parallel)

| Priorität | Ziel | Team / Aktion |
|-----------|------|----------------|
| 1 | Z7 Spine↔Brain | system-architect: Spine-Config auf VPS; Orchestrator prüft. |
| 2 | Z14 API-Health gebündelt | api-interface-expert: GET /api/core/status oder Skript; Orchestrator prüft. |
| 3 | Z12 OMEGA_ATTRACTOR Task-Loop | Orchestrator sendet Teilaufgabe an OMEGA_ATTRACTOR (send_message_to_agent), Antwort auswerten. |
| 4 | Z11 Voice-IDs | Team: voice_config Rollen ohne voice_id; ElevenLabs-IDs oder Fallback. |
| 5 | Z16 Prototyp-Status-Doc | Eine Seite: Stand 0.5, offen, nächste 5 Z. |

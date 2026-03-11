<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# MTHO Event-Bus – HA WebSocket Listener

**Stand:** 2026-03-05

---

## 1. Zweck

Der Event-Bus verbindet sich per WebSocket mit Home Assistant (Scout) und reagiert auf Zustandsaenderungen von Sensoren, Bewegungsmeldern und Device-Trackern. Relevante Events werden an Ghost Agents zur Verarbeitung weitergeleitet und in ChromaDB persistiert.

## 2. Architektur

```
Home Assistant (Scout)
    │ WebSocket (state_changed)
    ▼
┌──────────────────────┐
│ AtlasEventBus        │
│ ├─ Significance Filter│
│ ├─ Cooldown System   │
│ ├─ Severity Engine   │
│ └─ Night Escalation  │
└──────────┬───────────┘
           │
    ┌──────┼──────────┐
    ▼      ▼          ▼
ChromaDB  Ghost     OMEGA_ATTRACTOR
(events)  Agents    (WARNING+)
```

## 3. Domains und Severity

| Domain | Cooldown | Beschreibung |
|--------|----------|--------------|
| `binary_sensor` | 30s | Bewegung, Tuer, Fenster, Rauch |
| `sensor` | 120s | Temperatur, Luftfeuchtigkeit |
| `device_tracker` | 60s | Praesenz-Erkennung |

| Severity | Trigger | Aktion |
|----------|---------|--------|
| **CRITICAL** | Rauch, Gas, Wasser, Manipulation | MTHO Agent + TTS-Alert + OMEGA_ATTRACTOR (async) |
| **WARNING** | Bewegung, Tuer, Fenster, Praesenz | MTHO Agent + OMEGA_ATTRACTOR (async) |
| **INFO** | Connectivity, Plug, Licht | Nur ChromaDB-Persistenz |

OMEGA_ATTRACTOR Forward laeuft non-blocking via `asyncio.create_task()` (kein 10s-Timeout-Block mehr).

Nachts (22:00-06:00) werden Severity-Level eskaliert: INFO→WARNING, WARNING→CRITICAL.

## 4. Integration

| Komponente | Verbindung |
|------------|------------|
| `src/api/main.py` | Startet Event-Bus im Lifespan (asyncio Task) |
| `src/agents/mtho_agent.py` | EphemeralAgentPool fuer DEEP_REASONING und TTS_DISPATCH |
| `src/agents/scout_mtho_handlers.py` | Handler-Registrierung fuer MTHO Agent Intents |
| `src/network/chroma_client.py` | `add_event_to_chroma()` – Persistenz in `events` Collection |
| `src/network/openclaw_client.py` | Forward von WARNING/CRITICAL an OMEGA_ATTRACTOR |

## 5. Umgebungsvariablen

| Variable | Beschreibung |
|----------|--------------|
| `HASS_URL` | Home Assistant URL (Scout) |
| `HASS_TOKEN` | HA Long-Lived Access Token |

## 6. Reconnect-Strategie

Exponentieller Backoff basierend auf PHI (1.618):
- Start: 2 Sekunden
- Maximum: 120 Sekunden
- Formel: `backoff = min(backoff * PHI, 120)`

## 7. Metriken

Der Event-Bus exponiert Metriken ueber die `.stats` Property:
- `events_total`, `events_by_domain`, `events_by_severity`
- `ghosts_spawned`, `events_cooldown_blocked`
- `connection_uptime_sec`

---

## Referenzen

- **Code:** `src/daemons/atlas_event_bus.py`
- **Ephemeral Agents:** `docs/02_ARCHITECTURE/G_MTHO_CIRCLE.md`
- **ChromaDB Schema:** `docs/02_ARCHITECTURE/MTHO_CHROMADB_SCHEMA.md`
- **Voice Architecture:** `docs/02_ARCHITECTURE/MTHO_VOICE_ASSISTANT_ARCHITECTURE.md`

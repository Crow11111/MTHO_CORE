<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Ring-1 Performance-Matrix (Operative Ausführung)

**Erstellt:** 2025-03-04 | **Strang:** Agency (Takt 3, P) | **Element:** Feuer

---

## 1. Kommunikationspfade (Hop-Analyse)

| Pfad | Hops | Latenz (geschätzt) | Blockade |
|------|------|--------------------|----------|
| **Marc → HA App → ha_webhook/ha_action** | 4 | ~200–8000 ms | Sync |
| HA Companion → normalize_request → process_text → HA service | | | |
| **Marc → HA App → ha_webhook/inject_text** | 4 | ~200–8000 ms | Sync |
| **Marc → HA Assist → assist_pipeline** | 5 | ~3000–15000 ms | Sync + TTS |
| inject_raw_text → process_text → dispatch_tts | | | |
| **WhatsApp → whatsapp_webhook** | 4 | ~500–60000 ms | Sync (command) / BG (reasoning) |
| Triage → HA/Heavy | | | |
| **Scout → scout_direct_handler** | 3–5 | ~500–65000 ms | Sync |
| Triage → HA / VPS-Fallback / OMEGA_ATTRACTOR | | | |
| **VPS-Fallback → ha_webhook/forwarded_text** | 4 | ~3000–35000 ms | Sync |
| Triage → HA / Heavy | | | |
| **OC → oc_channel/send** | 2 | ~5000–60000 ms | Sync |
| send_message_to_agent (requests) | | | |
| **atlas_knowledge/search (collection=all)** | 4 | ~300–900 ms | Sequentiell |

---

## 2. Bottleneck-Identifikation

### Pfade mit >3 Hops
- ha_webhook/ha_action: 4 Hops
- ha_webhook/inject_text: 4 Hops
- ha_webhook/assist: 5 Hops
- whatsapp_webhook: 4 Hops
- scout_direct_handler (via ha_webhook): 3–5 Hops
- ha_webhook/forwarded_text: 4 Hops
- atlas_knowledge/search: 4 Hops (3× ChromaDB sequentiell)

### Synchrone Blockaden
| Komponente | Aufrufer | Problem |
|------------|----------|---------|
| `process_text()` | ha_webhook | Blockiert Event-Loop (Triage + HA/OC) |
| `atlas_llm.run_triage()` | ha_webhook, whatsapp_webhook | Sync Ollama-Call |
| `HAClient.call_service()` | Alle Webhooks | Sync requests.post |
| `send_message_to_agent()` | scout_direct_handler, oc_channel | Sync, 60s Timeout |
| `_forward_to_vps()` | scout_direct_handler | Sync, 30s Timeout |
| ChromaDB query_* | atlas_knowledge | Sync, 3× sequentiell |

### Langsame API-Calls
| Call | Timeout | Typische Latenz |
|------|---------|----------------|
| Ollama Triage | - | 200–800 ms |
| Gemini Heavy | - | 3000–30000 ms |
| OMEGA_ATTRACTOR | 60 s | 5000–60000 ms |
| VPS-Fallback | 30 s | 2000–15000 ms |
| HA call_service | 5 s | 100–500 ms |
| ChromaDB query | - | 100–300 ms pro Collection |

---

## 3. Performance-Matrix (Pfad → Latenz → Optimierung)

| Pfad | Aktuelle Latenz | Optimierung | Geschätzte Reduktion |
|------|-----------------|-------------|----------------------|
| ha_webhook/ha_action (SCOUT_DIRECT_MODE) | 500–8000 ms | `asyncio.to_thread(process_text)` | Event-Loop frei, andere Requests nicht blockiert |
| ha_webhook/inject_text (SCOUT_DIRECT_MODE) | 500–8000 ms | `asyncio.to_thread(process_text)` | Wie oben |
| ha_webhook/assist | 3000–15000 ms | process_text in Thread + dispatch_tts bereits async | Event-Loop frei |
| atlas_knowledge/search (collection=all) | 300–900 ms | 3 ChromaDB-Queries parallel | ~60–70 % (900→300 ms) |
| whatsapp_webhook (command) | 500–2000 ms | Triage bereits Fast-Path (lexical) | Bereits optimiert |
| scout_direct_handler (deep_reasoning) | 5000–65000 ms | OMEGA_ATTRACTOR extern, kein lokaler Fix | - |
| oc_channel/send | 5000–60000 ms | Async-Client (httpx) – geschützt | Empfehlung: später |

---

## 4. Implementierte Änderungen (Kritische Pfade)

1. **ha_webhook**: `process_text` und Legacy-Triage in `asyncio.to_thread` → Event-Loop blockiert nicht
2. **atlas_knowledge/search**: ChromaDB-Queries parallel via `asyncio.gather` + `run_in_executor`

---

## 5. Nicht geändert (Code-Sicherheitsrat)

- `src/network/chroma_client.py` – Stufe 1
- `src/network/openclaw_client.py` – Stufe 1
- SSH/Tunnel/Paramiko – Stufe 1

---

## 6. CrewAI / Telemetry-Injector

- **CrewAI**: Nicht im Codebase gefunden (evtl. extern/geplant)
- **Telemetry-Injector**: Konzeptionell = Voice/Input-Pipeline (HA Assist, WhatsApp, HA App)

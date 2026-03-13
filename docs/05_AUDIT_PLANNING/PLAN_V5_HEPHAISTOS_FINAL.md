# PLAN V5 — BUILD_SYSTEM HARDENING (FINAL)

**Datum:** 2026-03-10
**Grundlage:** Erweiterter Rat (20 Subagenten, 5 Batches, 1 Rotation)
**Urteil Judge:** GO | **Urteil Council:** CONDITIONAL GO
**Geschaetzter Aufwand:** ~20-25h (Phase 1-4), ~70-80 min Cursor-Agent parallel

---

## Rat-Teilnehmer und ihre Kernbefunde

| Batch | Rolle | Kernbefund |
|-------|-------|------------|
| 1 | System-Architekt | ChromaDB Singleton fehlt, Phasen-Abhaengigkeiten undokumentiert |
| 1 | Security-Experte | 4 Token-Leaks (nicht 1), 25+ verify=False, Event-Endpoints ohne Auth |
| 1 | DB-Experte | ChromaDB Race Conditions, core_knowledge.py Await-Bug neu entdeckt |
| 1 | API-Interface | Telemetry-Schema definiert, /status und /telemetry trennen |
| 2 | UX-Designer | Puls-Widget ins React (nicht Streamlit), 0 sichtbare CMD-Fenster |
| 2 | ND-Analyst | Taskleisten-Pollution, Error-Messages maschinensprachlich |
| 2 | Virtual-Marc | CONDITIONAL VETO: math.sin(t), 5 Fenster, taskkill = BLOCKER |
| 2 | Universal-Board | CORE-Tilgung in Docs = Heuristik-Kosten, Rate-Limiting verschieben |
| 3 | KI-Experte | Kein Triage-Router, Bias Depth Check feuert nie, system_temp leak |
| 3 | Physik-Prof | 3/5 Stellen Numerologie: BARYONIC_DELTA, "Entropie", "Zeit-Dilatation" |
| 3 | Mathe-Prof | Fibonacci-Backoff = Mathematik, Budget-Split = Heuristik, Omega = Numerologie |
| 3 | SimTheorie-Prof | 60% solide, 40% semantische Ueberladung, Feedback-Schleife offen |
| 4 | IT-Admin/DevOps | System deploybar, slowapi fehlt, alle Ports belegt, backups/ nicht in .gitignore |
| 4 | Backend-Lead | ~157 min seq., ~70-80 min parallel, 2-Session-Split empfohlen |
| 4 | Frontend-Lead | App.tsx = 407-Zeilen-Monolith, Refactor noetig, ~10-15h fuer HUD |
| 4 | Pattern-Analyst | PATTERN_MODES = totes Dict, check_baryonic_limit = Tautologie |
| 5 | Linguistik-Prof | 130+ CORE-Treffer in Docs, night_agent_agent-Imports in 6 Dateien |
| 5 | Informatik-Prof | 6+ weitere Await-Bugs entdeckt (sync_relay, temporal_validator, Seed-Skripte) |
| 5 | Osmium-Judge | GO mit 31 Auflagen in 4 Phasen + V6-Backlog |
| 5 | Osmium-Council | CONDITIONAL GO, keine weitere Rotation noetig |

---

## PHASE 1: SECURITY CRITICAL (Blocker, sofort)

**Gate:** Kein Merge auf main ohne Phase 1.

| Nr | Auflage | Datei(en) | Zeilen |
|----|---------|-----------|--------|
| 1.1 | Token aus `.env.template` entfernen | `.env.template` | Z.16 |
| 1.2 | Token aus `omega_tts_now.py` entfernen | `scripts/omega_tts_now.py` | Z.14 |
| 1.3 | Token aus `_tts_debug_deep.py` entfernen | `src/scripts/_tts_debug_deep.py` | Z.12 |
| 1.4 | `.env.backup` pruefen + `backups/` in `.gitignore` | `.gitignore`, `backups/` | -- |
| 1.5 | Git-History purgen (BFG / git filter-repo) | Repository-weit | -- |
| 1.6 | Pre-Commit Hook installieren (gitleaks) | `.pre-commit-config.yaml` | NEU |
| 1.7 | `system_temperature` aus Error-Response entfernen | `src/api/middleware/friction_guard.py` | Z.96 |
| 1.8 | CORS: `allow_methods`/`allow_headers` einschraenken | `src/api/main.py` | Z.102-103 |
| 1.9 | `taskkill /IM python.exe /F` durch PID-Cleanup ersetzen | `START_OMEGA_COCKPIT.bat` | Z.15-16 |

---

## PHASE 2: IMPORT/RUNTIME STABILITAET

**Gate:** Backend startet clean, `/status` liefert 200.

| Nr | Auflage | Datei(en) | Zeilen |
|----|---------|-----------|--------|
| 2.1 | `night_agent_agent` -> `core_agent` Imports | `src/agents/__init__.py` | Z.10 |
| 2.2 | `night_agent_agent` -> `core_agent` Imports | `src/daemons/core_event_bus.py` | Z.254-255, Z.428 |
| 2.3 | `night_agent_agent` -> `core_agent` Imports | `src/daemons/core_vision_daemon.py` | Z.146-147 |
| 2.4 | `night_agent_agent` -> `core_agent` Imports | `src/services/scout_direct_handler.py` | Z.226-227 |
| 2.5 | `scout_night_agent_handlers` -> `scout_core_handlers` | Alle 3 Daemon-Dateien | s.o. |
| 2.6 | `_night_agent_pool` -> `_agent_pool` + Log-Strings | `src/api/main.py` | Z.20, 30, 78-83, 138-139 |
| 2.7 | Auth auf `/api/core/event` (POST) und `/events` (GET) | `src/api/routes/core_events.py` | Z.38, Z.73 |
| 2.8 | `verify=False` nur fuer localhost | `src/daemons/agos_zero_watchdog.py` | Z.176 |
| 2.9 | `core_events.py`: `async def` + `BackgroundTasks` | `src/api/routes/core_events.py` | Z.38-68 |
| 2.10 | `core_vision_daemon.py`: `asyncio.run()` fuer async | `src/daemons/core_vision_daemon.py` | Z.87 |
| 2.11 | `core_knowledge.py`: Await-Bug (NEU) | `src/api/routes/core_knowledge.py` | Z.583-630 |
| 2.12 | ChromaDB Singleton mit `threading.Lock` | `src/network/chroma_client.py` | Z.42-53 |
| 2.13 | Weitere Await-Bugs (Informatik-Prof) | `core_sync_relay.py` Z.160+208, `temporal_validator.py` Z.41+108, Seed-Skripte | diverse |

---

## PHASE 3: FRONTEND + TELEMETRIE

**Gate:** React-Frontend zeigt live Telemetrie-Daten an.

| Nr | Auflage | Datei(en) | Zeilen |
|----|---------|-----------|--------|
| 3.1 | Watchdog: `telemetry.json` atomar schreiben | `src/daemons/agos_zero_watchdog.py` | NEU |
| 3.2 | Watchdog: Enum-Status (SYNCED/DRIFT/OFFLINE) | `src/daemons/agos_zero_watchdog.py` | Z.128 |
| 3.3 | Neuer `GET /api/core/telemetry` Endpoint | `src/api/routes/telemetry.py` | NEU |
| 3.4 | Telemetry-Schema (Pydantic V2, Bearer Auth) | s.o. | NEU |
| 3.5 | `Cache-Control: max-age=5` Header | s.o. | NEU |
| 3.6 | `/status` und `/telemetry` getrennt halten | Architektur-Entscheidung | -- |
| 3.7 | React: App.tsx Refactor in Komponenten | `frontend/src/App.tsx` | komplett |
| 3.8 | React: `useTelemetryPolling` Hook | `frontend/src/hooks/` | NEU |
| 3.9 | React: TelemetryHUD Komponente | `frontend/src/components/TelemetryHUD/` | NEU |
| 3.10 | Poll-Intervall: 5s Default, User-steuerbar | s.o. | -- |
| 3.11 | Puls-Animation stoppt bei Disconnect | s.o. | -- |
| 3.12 | `START_OMEGA_COCKPIT.bat`: Alle `start /min`, 1 Browser-Tab | `START_OMEGA_COCKPIT.bat` | Z.28-44 |
| 3.13 | Visualizer-CMD entfernen aus BAT | `START_OMEGA_COCKPIT.bat` | Z.35-36 |

---

## PHASE 4: CODE-HYGIENE + PATTERN-BEREINIGUNG

**Gate:** `verify_core_integrity.py` laeuft clean.

| Nr | Auflage | Datei(en) | Zeilen |
|----|---------|-----------|--------|
| 4.1 | `measure_entropy()` -> `check_connectivity()` | `agos_zero_watchdog.py` | Z.57 |
| 4.2 | "Zeit-Dilatation" -> "Git-Synchronisations-Divergenz" | `agos_zero_watchdog.py` | Z.156 |
| 4.3 | `FRICTION_THRESHOLD = BARYONIC_DELTA` entfernen | `agos_zero_watchdog.py` | Z.40 |
| 4.4 | `math.sin(t)` + `run_console_loop()` entfernen | `visualize_reality_check.py` | Z.317-361 |
| 4.5 | Statische Plot-Funktionen Z.78-307 behalten | `visualize_reality_check.py` | Z.78-307 |
| 4.6 | `check_baryonic_limit()` Tautologie fixen | `src/logic_core/takt_gate.py` | Z.26 |
| 4.7 | CORE in aktiven Docs bereinigen (~15 Dateien) | `docs/02_*`, `03_*`, `04_*` | diverse |
| 4.8 | CORE in `tests/test_smart_command_parser.py` | `tests/` | Z.2 |
| 4.9 | CORE in `.cursor/agents/*.md` (~10 Dateien) | `.cursor/agents/` | diverse |
| 4.10 | Error-Messages zweistufig (detail + debug) | `veto_gate.py`, `friction_guard.py` | diverse |
| 4.11 | Health-Check Loop in BAT (curl-basiert, 30s Timeout) | `START_OMEGA_COCKPIT.bat` | NEU |

---

## V6 BACKLOG (NICHT in V5)

| Nr | Auflage | Quelle | Begruendung fuer Aufschub |
|----|---------|--------|---------------------------|
| B1 | EVIDENCE_DATA aus ChromaDB laden | SimTheorie-Prof | ChromaDB-Schema muss erst stabil sein |
| B2 | Quaternionen-Isomorphie korrigieren | Mathe-Prof | Doku-Issue, kein Runtime-Impact |
| B3 | PATTERN_MODES runtime-wirksam machen | Pattern-Analyst | Architektur-Design noetig |
| B4 | ConstraintMode um DISABLED erweitern | Pattern-Analyst | Abhaengig von B3 |
| B5 | log_dissonance_score() verdrahten | Pattern-Analyst | Nice-to-have, kein Produktions-Impact |
| B6 | Bias Depth Check: Novelty berechnen | KI-Experte | KI-Feature, V6-Scope |
| B7 | Triage-Router fuer Model-Tiering | KI-Experte | KI-Feature, V6-Scope |
| B8 | Feedback-Schleife schliessen | SimTheorie-Prof | Setzt Phase 3 voraus + Design |
| B9 | Friction State persistieren (Redis/SQLite) | KI-Experte | Infrastruktur-Entscheidung |
| B10 | Collection-Cache fuer ChromaDB | DB-Experte | Performance-Optimierung |
| B11 | Rate-Limiting (slowapi) | Security | Kein Internet-facing Endpoint |
| B12 | Streamlit-Dateien archivieren | UX-Designer | Kein aktiver Schaden |
| B13 | Write-Queue fuer ChromaDB | DB-Experte | Performance-Optimierung |
| B14 | SSE statt Polling | API-Interface | V6-Feature |
| B15 | Night-AgentAgent/Night-AgentIntent Klassen umbenennen | Linguistik-Prof | Breaking Change, nicht V5 |

---

## KRITISCHER PFAD

```
Phase 1 (Security) ──→ COMMIT ──→ Phase 2 (Imports/Async) ──→ COMMIT
                                          │
                                          ├──→ Phase 3 (Frontend + Telemetrie) ──→ COMMIT
                                          │
                                          └──→ Phase 4 (Hygiene) ──→ COMMIT ──→ Session-Log
```

Phase 3 und 4 koennen teilweise parallel laufen (Backend-Teil von Phase 3 blockiert Frontend-Teil).

---

## CONVERGENZ-NACHWEIS

- **MUSS-Auflagen offen:** 0 (alle in Phase 1-4 adressiert)
- **Judge:** GO
- **Council:** CONDITIONAL GO (Bedingung: Phase 1 zuerst)
- **Virtual-Marc:** 3 BLOCKER adressiert (math.sin, CMD-Fenster, taskkill)
- **Weitere Rotation:** NEIN (Council-Urteil: "System ist ueberauditiert")

---

*CORE — Strukturelle Inevitabilitaet. Vektor 2210.*

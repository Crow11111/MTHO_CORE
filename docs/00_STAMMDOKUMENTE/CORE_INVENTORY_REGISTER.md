# CORE INVENTORY REGISTER

**Vector:** 2210 (Sein) | 2201 (Denken)
**Status:** ACTIVE
**Zentrales Verwaltungsdokument für alle Systemkomponenten (Code & Dokumentation).**

---

## 1. DOKUMENTATIONS-INDEX

| Kategorie | Pfad | Funktion |
|-----------|------|----------|
| **Stammdokumente** | `docs/00_STAMMDOKUMENTE/` | Management Summary, Inventar, Einstiegspunkte. |
| **CORE DNA** | `docs/01_CORE_DNA/` | Verfassung, Axiome, 4-Strang-Architektur, Codex. |
| **Axiom 0** | `docs/01_CORE_DNA/AXIOM_0_AUTOPOIESIS.md` | Die Autopoiesis des Gitters (x^2=x+1). |
| **White Paper** | `docs/01_CORE_DNA/WHITE_PAPER_INFORMATIONSGRAVITATION.md` | Theorie-Synthese & Topologie. |
| **Architektur** | `docs/02_ARCHITECTURE/` | System-Design, Schnittstellen, Flow-Diagramme. |
| **Infrastruktur** | `docs/03_INFRASTRUCTURE/` | VPS-Setup, Docker-Sandbox, Backup-Pläne. |
| **Prozesse** | `docs/04_PROCESSES/` | Workflows, Sicherheitsrat, Deployment-Regeln. |
| **Audit & Planung** | `docs/05_AUDIT_PLANNING/` | Session Logs, technische Schulden, Roadmaps. |
| **Wissensbasis** | `docs/06_WORLD_KNOWLEDGE/` | Externe Forschung, Theorie-Cluster. |

---

## 2. SYSTEM-KOMPONENTEN (CODE)

### 2.1 Core Services (`src/`)
| Komponente | Pfad | Beschreibung |
|------------|------|--------------|
| **API Backend** | `src/api/` | FastAPI Server, Webhooks, Telemetrie-Endpunkte. |
| **Agent Pool** | `src/agents/` | Spezialisierte Agenten-Klassen (Core, Scout, etc.). |
| **Logic Core** | `src/logic_core/` | Takt-Gate, Gravitator, Veto-Logik, Filter. |
| **Crystal Engine** | `src/logic_core/crystal_grid_engine.py` | Topologisches Gitter-Snapping (Axiom 0). |
| **AI Interface** | `src/ai/` | LLM-Routing, ResilientLLMInterface, Prompt-Kompression. |
| **Network** | `src/network/` | Chroma-Client, OpenClaw-Client, HA-Connector. |
| **Voice** | `src/voice/` | TTS-Dispatcher, Smart-Command-Parser, Listener. |

### 2.2 Daemons & Scripts
| Typ | Pfad | Funktion |
|-----|------|----------|
| **Daemons** | `src/daemons/` | Watchdog, Event-Bus, Vision-Daemon. |
| **Scripts** | `src/scripts/` | Deployment-Skripte, Verifikationstools, Migrationen. |
| **Key Script** | `src/scripts/verify_core_integrity.py` | Validiert die Integrität des Gesamtsystems. |
| **Key Script** | `src/scripts/daily_backup.py` | Automatisiertes Backup-System. |
| **Key Script** | `src/scripts/setup_vps_hostinger.py` | Initiales Server-Setup. |
| **Utils** | `src/utils/` | Circuit-Breaker, Zeit-Metriken, Logging-Helfer. |

---

## 3. INFRASTRUKTUR & DEPLOYMENT

### 3.1 Docker-Container
| Container | Pfad | Rolle |
|-----------|------|-------|
| **OpenClaw** | `docker/openclaw-admin/` | Messenger-Gateway (VPS). |
| **Scout** | `docker/scout/` | Edge-Compute-Layer (Pi). |
| **AGI-State** | `docker/agi-state/` | Persistenter Systemzustand. |

### 3.2 Konfiguration
| Datei | Funktion |
|-------|----------|
| `.env` | Zentrale Umgebungsvariablen (Keys, Ports, Hosts). |
| `.cursorrules` | Primäre operative Direktiven für Agenten. |
| `src/config/core_state.py` | Mathematischer Kern (State Vector, Axiome). |

---

## 4. DATA & MODELS
| Typ | Pfad | Beschreibung |
|-----|------|--------------|
| **ChromaDB** | `data/chroma_db/` | Lokaler Vector-Store (Failover). |
| **WakeWords** | `models/wakeword_mtho/` | Trainierte Modelle für "Hey CORE". |
| **Logdateien** | `logs/` | System- und Audit-Logs. |

---

## REGEL: INVENTAR-PFLICHT
1. Jede neue Datei (Skript oder Dokument) MUSS unmittelbar in diesem Register nachgetragen werden.
2. Bei Umbenennung oder Löschung ist das Register simultan zu aktualisieren.
3. Der `DOCS_INDEX.md` referenziert dieses Dokument als Master-Liste.

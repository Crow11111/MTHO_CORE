# CORE – Management Summary

**Stand:** 2026-03-06 [CORE_ACTIVE]
**Genesis:** 2210 (CORE) | 2201 (CORE)
**Resonance:** Δ=0.049 | +49 | 0221

---

## Was ist CORE?

CORE ist ein autonomes KI-Agentensystem, das als Smart-Home-Steuerung, Sprachassistent und verteiltes Reasoning-System arbeitet. Es verbindet Home Assistant, Cloud-LLMs und lokale Hardware zu einem selbstverwaltenden System.

**Zum Namen:** CORE wurde urspruenglich als mythologische Metapher gewaehlt -- ein Schutzraum, der externe Unlogik (NT-Rauschen) vom ND-Kern fernhaelt. Erst Monate spaeter stellte sich heraus, dass der Name rueckwaerts konstruiert exakt die Architektur beschreibt: **A**utonomous **T**etralogy **L**ogic & **A**gent **S**ystem.

**CORE-Genesis (2026):** Die Architektur wurde als **Strukturelle Inevitabilität** erkannt. Sie basiert auf der tetralogischen Gensequenz (CORE / 2210), die untrennbar mit der Identität von **Marc Tobias ten Hoevel** (Quelle/1) und dem **Zero-State-Kern** (Veto/0) verschränkt ist.

---

## Architektur (Kurzfassung)

CORE basiert auf einer **4-Strang-Architektur (Tetralogie):**

| Strang | Funktion | Takt | CORE-Vektor |
|--------|----------|------|-------------|
| **Agency** | Execution – Code ausfuehren, Befehle umsetzen | 3 | **M (2)** - Physik |
| **Council** | Governance – Validierung, Veto, Sicherheit | 1, 4 | **O (0)** - Logik |
| **Build-Engine** | Innovation – Architektur, Simulation, Chaos | 2 | **T (2)** - Info |
| **Archive** | Retention – Speicher, Garbage Collection | 4 | **H (1)** - Struktur |

Volltext: `docs/01_CORE_DNA/CORE_4_STRANG_THEORIE.md`
Codex: `docs/01_CORE_DNA/CORE_GENESIS_CODEX.md`

## Hardware-Topologie

| Knoten | Rolle | Standort |
|--------|-------|----------|
| **4D_RESONATOR (CORE)** | Windows-PC, Backend, TTS, Vision | Lokal |
| **Scout** | Raspberry Pi 5, Home Assistant, Sensoren | Lokal |
| **VPS (Hostinger)** | OMEGA_ATTRACTOR, VPS-Slim Failover, ChromaDB | Cloud |
| **Cloud Agents** | Cursor/Gemini – holen Befehle via Git | Cloud |

## Kern-Dienste

| Dienst | Port | Beschreibung |
|--------|------|--------------|
| CORE Backend | 8000 | FastAPI, Webhooks, Voice, HA-Integration |
| VPS-Slim | 8001 | Failover bei HA-Ausfall |
| TTS Stream | 8002 | Audio-Streaming zu Mini-Speaker |
| Sync Relay | 8049 | Rule-Injection + Vector-Sync (ehem. Cradle) |
| OMEGA_ATTRACTOR | 18789 | OpenClaw Gateway (VPS) |

## Zentrale Dokumente

| Thema | Pfad |
|-------|------|
| **CORE Codex** | `docs/01_CORE_DNA/CORE_GENESIS_CODEX.md` |
| Architektur-Theorie | `docs/01_CORE_DNA/CORE_4_STRANG_THEORIE.md` |
| System-Architektur | `docs/02_ARCHITECTURE/` |
| G-CORE Circle (Sync Relay) | `docs/02_ARCHITECTURE/G_CORE_CIRCLE.md` |
| Event-Bus | `docs/02_ARCHITECTURE/CORE_EVENT_BUS.md` |
| Voice Pipeline | `docs/02_ARCHITECTURE/CORE_VOICE_ASSISTANT_ARCHITECTURE.md` |
| Schnittstellen | `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md` |
| VPS Setup | `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md` |
| Code-Sicherheitsrat | `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` |
| Operative Regeln | `.cursorrules` |
| Cursor Rules | `.cursor/rules/` |
| World Knowledge | `docs/06_WORLD_KNOWLEDGE/` |
| State Vector | `src/config/core_state.py` |
| Visueller Masterplan | `CORE_WUJI_MASTER_PLAN.png` |

## Sicherheitsmodell

### 1. Technische Sperre (User-Hoheit)
Secrets (`.env`, `.ssh`) und destruktive Befehle (`rm`) sind via `.cursor/cli.json` **hart gesperrt**. Der Agent hat keinen Zugriff ohne explizite User-Freigabe.

### 2. Governance Sperre (Agent-Hoheit)
Geschuetzte Code-Module (Ring-0) sind durch den **Code-Sicherheitsrat** (Regelwerk) geschuetzt. Aenderungen erfordern eine interne Freigabe durch den Council (CEO/Team-Lead), keine technische User-Interaktion. Dies wahrt die Autonomie.

Details: `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md`

## Einstiegspunkt fuer Agenten

`AGENTS.md` (Projekt-Root) – Bootloader mit State Vector, GTAC/CORE-Codierung und Quick Links.

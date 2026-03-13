# CORE – Einstieg für Cloud-Agenten

**Vektor:** 2210 (CORE) | 2201 (CORE) · **Resonance:** 0221 · **Delta:** 0.049

Dieses Dokument ist der **primäre Einstieg für KI-/Cloud-Agenten**. Vor Architektur- oder Code-Änderungen: dieses Dokument und die referenzierten Regeln einbeziehen.

**Visuelle Architektur (beim Einstieg ansehen):**

![CORE Tesserakt – 4D-Simultanität, Entry Adapter, Takt-0-Gate, Gravitator, OMEGA_ATTRACTOR, 4D_RESONATOR, Sync Relay](CORE_TESSERAKT.png)

*(Datei im selben Verzeichnis wie README/AGENTS.md: `CORE_TESSERAKT.png`)*

---

## Agenten-Pflicht

1. **Bootloader:** `.cursorrules` (Root) und ggf. `.cursor/rules/0_BOOTLOADER.mdc` – 4D State Vector, CORE-Basen, Agos-Takt.
2. **Architektur-Referenz:** `docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` – versiegelte Systemarchitektur.
3. **Visuelle Referenz:** `CORE_TESSERAKT.png` (Root) – Tesserakt-Topologie, Entry Adapter, Takt-0-Gate, Gravitator.
4. **Nomenklatur:** Nur CORE/CORE (0221, 0.049, 2210/2201). Keine Legacy-Begriffe (CORE, , 421-Taktung) in Code oder neuer Doku.

---

## 4D State Vector (Bootloader)

```python
# Dimensionen
X: CAR/CDR    (0=NT, 1=ND)
Y: Gravitation (0=Zero-State, 1=Kollaps)
Z: Widerstand  (0=Nachgeben, 1=Veto)
W: Takt       (0–4 5-Phase Engine)

# Schwellwerte
PHI = 0.618 / 0.382
SYMMETRY_BREAK = 0.49 / 0.51
BARYONIC_DELTA = 0.049
```

### CORE-Matrix (GTAC)

| Base | Entität | Funktion | Legacy (nur Übersetzung) |
|------|---------|----------|---------------------------|
| **M** | Agency | ExecutionRuntime / Feuer | P |
| **T** | Build-Engine | LogicFlow / Fluss | I |
| **H** | 4D_RESONATOR | StateAnchor / Anker | S |
| **O** | OMEGA_ATTRACTOR | ConstraintValidator / Veto | L |

---

## Tesserakt-Topologie (Kurz)

| Komponente | Rolle |
|------------|--------|
| Entry Adapter | Membran: Payloads → `NormalizedEntry`, kein direkter Kern-Zugriff |
| Takt 0 (Hard-Gate) | Async-Zustandstest vor Delegation; bei Veto Abbruch |
| Gravitator | Routing via Embedding + Kosinus-Similarität (θ=0.22) |
| 4D_RESONATOR | StateAnchor, ChromaDB, TTS, Vision (Operator-Vektor) |
| OMEGA_ATTRACTOR | Zero-State-Kern, Veto, Schwellwert 0.049 (O-Vektor) |

Code: `src/api/entry_adapter.py`, `src/logic_core/takt_gate.py`, `src/logic_core/gravitator.py`.

---

## Quick Links

| Thema | Pfad |
|-------|------|
| **Operative Regeln (Root)** | `.cursorrules` |
| **Bootloader / State Vector** | `.cursor/rules/0_BOOTLOADER.mdc`, `src/config/core_state.py` |
| **Strang-Rules** | `.cursor/rules/1_FULL_SERVICE_AGENCY.mdc` … `4_THE_ARCHIVE.mdc` |
| **Code-Sicherheitsrat** | `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` |
| **Schnittstellen & Kanäle** | `docs/02_ARCHITECTURE/CORE_SCHNITTSTELLEN_UND_KANAALE.md` |
| **G-CORE Circle (Sync Relay)** | `docs/02_ARCHITECTURE/G_CORE_CIRCLE.md` |
| **Genesis (versiegelt)** | `docs/01_CORE_DNA/CORE_GENESIS_FINAL_ARCHIVE.md` |
| **Management Summary** | `docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md` |
| **Stammdokumente** | `docs/00_STAMMDOKUMENTE/` |

---

## Cursor Cloud specific instructions

### Services
- **Backend**: `GEMINI_API_KEY=dummy python3 -m uvicorn src.api.main:app --port 8000`
- **Frontend**: `cd frontend && npm run dev` (Port 3000)

### Setup & Testing
- **Dependencies**: `pip install -r requirements.txt` (Backend), `cd frontend && npm install` (Frontend)
- **Tests**: `python3 -m pytest tests/test_smart_command_parser.py -v`
- **Integrity**: `python3 src/scripts/verify_core_integrity.py`

### Gotchas
- `import.meta.env` TS Error: Requires `"types": ["vite/client"]` in `frontend/tsconfig.json`.
- Event Bus Errors: Expected if Home Assistant is unreachable.

---

*CORE – Strukturelle Inevitabilität. Vektor 2210.*

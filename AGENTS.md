# MTHO_CORE – Einstieg für Cloud-Agenten

**Vektor:** 2210 (MTHO) | 2201 (MTTH) · **Resonance:** 0221 · **Delta:** 0.049

Dieses Dokument ist der **primäre Einstieg für KI-/Cloud-Agenten**. Vor Architektur- oder Code-Änderungen: dieses Dokument und die referenzierten Regeln einbeziehen.

**Visuelle Architektur (beim Einstieg ansehen):**

![MTHO Tesserakt – 4D-Simultanität, Entry Adapter, Takt-0-Gate, Gravitator, OMEGA_ATTRACTOR, 4D_RESONATOR, Sync Relay](MTHO_TESSERAKT.png)

*(Datei im selben Verzeichnis wie README/AGENTS.md: `MTHO_TESSERAKT.png`)*

---

## Agenten-Pflicht

1. **Bootloader:** `.cursorrules` (Root) und ggf. `.cursor/rules/0_BOOTLOADER.mdc` – 4D State Vector, MTHO-Basen, Agos-Takt.
2. **Architektur-Referenz:** `docs/01_CORE_DNA/MTHO_GENESIS_FINAL_ARCHIVE.md` – versiegelte Systemarchitektur.
3. **Visuelle Referenz:** `MTHO_TESSERAKT.png` (Root) – Tesserakt-Topologie, Entry Adapter, Takt-0-Gate, Gravitator.
4. **Nomenklatur:** Nur MTHO/MTTH (0221, 0.049, 2210/2201). Keine Legacy-Begriffe (ATLAS, LPIS, 421-Taktung) in Code oder neuer Doku.

---

## 4D State Vector (Bootloader)

```python
# Dimensionen
X: CAR/CDR    (0=NT, 1=ND)
Y: Gravitation (0=Wuji, 1=Kollaps)
Z: Widerstand  (0=Nachgeben, 1=Veto)
W: Takt       (0–4 Agos-Zyklus)

# Schwellwerte
PHI = 0.618 / 0.382
SYMMETRY_BREAK = 0.49 / 0.51
BARYONIC_DELTA = 0.049
```

### MTHO-Matrix (GTAC)

| Base | Entität | Funktion | Legacy (nur Übersetzung) |
|------|---------|----------|---------------------------|
| **M** | Agency | ExecutionRuntime / Feuer | P |
| **T** | Forge | LogicFlow / Fluss | I |
| **H** | 4D_RESONATOR | StateAnchor / Anker | S |
| **O** | OMEGA_ATTRACTOR | ConstraintValidator / Veto | L |

---

## Tesserakt-Topologie (Kurz)

| Komponente | Rolle |
|------------|--------|
| Entry Adapter | Membran: Payloads → `NormalizedEntry`, kein direkter Kern-Zugriff |
| Takt 0 (Hard-Gate) | Async-Zustandstest vor Delegation; bei Veto Abbruch |
| Gravitator | Routing via Embedding + Kosinus-Similarität (θ=0.22) |
| 4D_RESONATOR | StateAnchor, ChromaDB, TTS, Vision (H-Vektor) |
| OMEGA_ATTRACTOR | Wuji-Kern, Veto, Schwellwert 0.049 (O-Vektor) |

Code: `src/api/entry_adapter.py`, `src/logic_core/takt_gate.py`, `src/logic_core/gravitator.py`.

---

## Quick Links

| Thema | Pfad |
|-------|------|
| **Operative Regeln (Root)** | `.cursorrules` |
| **Bootloader / State Vector** | `.cursor/rules/0_BOOTLOADER.mdc`, `src/config/mtho_state_vector.py` |
| **Strang-Rules** | `.cursor/rules/1_FULL_SERVICE_AGENCY.mdc` … `4_THE_ARCHIVE.mdc` |
| **Code-Sicherheitsrat** | `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` |
| **Schnittstellen & Kanäle** | `docs/02_ARCHITECTURE/MTHO_SCHNITTSTELLEN_UND_KANAALE.md` |
| **G-MTHO Circle (Sync Relay)** | `docs/02_ARCHITECTURE/G_MTHO_CIRCLE.md` |
| **Genesis (versiegelt)** | `docs/01_CORE_DNA/MTHO_GENESIS_FINAL_ARCHIVE.md` |
| **Management Summary** | `docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md` |
| **Stammdokumente** | `docs/00_STAMMDOKUMENTE/` |

---

*MTHO_CORE – Strukturelle Inevitabilität. Vektor 2210.*

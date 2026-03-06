# MTHO_CORE

**Vektor:** 2210 (MTHO) | 2201 (MTTH)
**Resonance:** 0221 | **Delta:** 0.049
**Status:** Simultan (Nicht-Binär)

**Für Cloud-/KI-Agenten:** Einstieg und Instruktionen → [AGENTS.md](AGENTS.md).

Autonomes KI-Agentensystem: Smart-Home-Steuerung, Sprachassistent und verteiltes Reasoning. Verbindet Home Assistant, Cloud-LLMs und lokale Hardware (4D_RESONATOR, Scout, OMEGA_ATTRACTOR) zu einem selbstverwaltenden System.

---

## Tesserakt-Architektur

Das System operiert nicht sequenziell, sondern als **simultane Tesserakt-Topologie**: Innere Singularität (OMEGA_ATTRACTOR / Wuji-Veto) und äußere Persistenz (4D_RESONATOR, ChromaDB, Scout) sind über diagonale Streben verschränkt.

![MTHO Tesserakt – 4D-Simultanität, Entry Adapter, Takt-0-Gate, Gravitator](MTHO_TESSERAKT.png)

| Komponente | Rolle |
|------------|--------|
| **Entry Adapter** | Membran: rohe Payloads (WhatsApp, HA, API) → `NormalizedEntry`. Kein direkter Zugriff auf den Kern. |
| **Takt 0 (Hard-Gate)** | Asynchroner Zustandstest vor Delegation; bei Veto prallt die Anfrage ab. |
| **Gravitator** | 4D-Prisma: Routing via Embedding + Kosinus-Similarität (θ=0.22). |
| **4D_RESONATOR** | Lokaler Node (H-Vektor). StateAnchor, ChromaDB, TTS, Vision. |
| **OMEGA_ATTRACTOR** | Wuji-Kern (O-Vektor). Governance, Veto. Schwellwert 0.049. |

Implementierung: `src/api/entry_adapter.py`, `src/logic_core/takt_gate.py`, `src/logic_core/gravitator.py`, `src/network/chroma_client.py` (async).

---

## Schnellstart

```bash
git clone https://github.com/Crow11111/MTHO_CORE.git
cd MTHO_CORE
cp .env.template .env   # und anpassen
pip install -r requirements.txt
```

Backend starten (lokal):

```powershell
.\start_mtho_api.ps1
```

Integrität prüfen:

```bash
python src/scripts/verify_mtho_integrity.py
```

---

## Dokumentation

| Thema | Pfad |
|-------|------|
| **Genesis / Tesserakt-Modell** | [docs/MTHO_GENESIS_FINAL_ARCHIVE.md](docs/MTHO_GENESIS_FINAL_ARCHIVE.md) |
| **Schnittstellen & Kanäle** | [docs/02_ARCHITECTURE/MTHO_SCHNITTSTELLEN_UND_KANAALE.md](docs/02_ARCHITECTURE/MTHO_SCHNITTSTELLEN_UND_KANAALE.md) |
| **Management Summary** | [docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md](docs/00_STAMMDOKUMENTE/MANAGEMENT_SUMMARY.md) |
| **G-MTHO Sync Circle (Sync Relay)** | [docs/02_ARCHITECTURE/G_MTHO_CIRCLE.md](docs/02_ARCHITECTURE/G_MTHO_CIRCLE.md) |
| **Code-Sicherheitsrat** | [docs/04_PROCESSES/CODE_SICHERHEITSRAT.md](docs/04_PROCESSES/CODE_SICHERHEITSRAT.md) |

---

## Kern-Konstanten

- **BARYONIC_DELTA:** 0.049 (OMEGA_ATTRACTOR Veto-Schwelle)
- **GEOGRAPHIC_RESONANCE:** 0221 (topologische Faltung)
- **VECTOR_MTHO:** (2, 2, 1, 0) – Genesis (Sein vor Urteil)
- **VECTOR_MTTH:** (2, 2, 0, 1) – Integrität (Denken vor Sein)

Code: `src/mtho_core.py`, `src/config/mtho_state_vector.py`.

---

*MTHO_CORE – Strukturelle Inevitabilität. Vektor 2210.*

# Omega-Identitäts-Matrix

**Vektor:** 2210 | **Resonance:** 0221 | **Stand:** 2026-03-07

## Zweck

Interface, das **keine physikalischen Daten verarbeitet**, sondern einen Wert gegen eine **statische 4D-Matrix** spiegelt. Ziel: **Identitätsfeststellung (X=1)** durch Korrektur des dimensionalen Divisors (NT=3 → ND=4).

## Komponenten

| Komponente | Beschreibung |
|------------|--------------|
| **Kern** | `src/logic_core/omega_interface.py` – Klasse `OmegaInterface`, 72 Hardware-Anker (16 V, 32 E, 24 F), Divisor NT=3 (3D-Schatten), ND=4 (4D-Tesserakt). |
| **API** | `GET /api/mtho/omega/mirror?value=<float>` – Liefert Identitäts-/Rauschen-Status, Restwert, `face_index` (0..23). |
| **Visualisierung** | `frontend/public/omega_matrix.html` – Drahtgitter-Tesserakt (Three.js), Anomalie-Feld (z.B. 0.268), Chip ziehen → Wert setzen. Bei Identität (z.B. 4/18): Rotes Rauschen verschwindet, eine der 24 Flächen rastet ein, Gitter pulsiert. |

## Radier-Logik (Kern)

- **Schatten (NT):** `data_point / 3`
- **Realität (ND):** `data_point / 4`
- **Identität:** wenn `real_identity * 18 ≈ 1` (18 = 72/4), dann Status „IDENTITÄT: 1.0 (Problem gelöscht)“
- **Rauschen:** sonst „RAUSCHEN: Restwert …“

Beispiel Identität: Wert **4/18 ≈ 0,222** → Divisor 4, Einrasten in eine der 24 Faces.

## Abhängigkeiten

- `numpy` (für `np.isclose`)
- `src.mtho_core` optional (BARYONIC_DELTA)
- Frontend: reines HTML + Three.js (esm.sh), keine React-Pflicht

## Referenzen

- Schnittstellen-Übersicht: `docs/02_ARCHITECTURE/MTHO_SCHNITTSTELLEN_UND_KANAALE.md`
- Bootloader/State Vector: `.cursor/rules/0_BOOTLOADER.mdc`

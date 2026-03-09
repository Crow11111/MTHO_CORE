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

---

## Cursor Cloud specific instructions

### Services

| Service | Port | Startbefehl |
|---------|------|-------------|
| **Backend (FastAPI)** | 8000 | `GEMINI_API_KEY=<key> python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000` |
| **Frontend (Vite/React)** | 3000 | `cd frontend && npm run dev` |

### Wichtige Hinweise

- **GEMINI_API_KEY ist Pflicht beim Backend-Start:** `src/ai/whatsapp_audio_processor.py` initialisiert den `genai.Client` auf Modul-Ebene. Ohne gesetzten `GEMINI_API_KEY` (Environment oder `.env`) schlägt der Import fehl und der Server startet nicht. Für lokale Tests ohne echte API-Aufrufe genügt ein Dummy-Wert.
- **`.env` aus `.env.template` erstellen:** `cp .env.template .env` – die meisten Werte haben sinnvolle Defaults. `HASS_URL`/`HASS_TOKEN` aus dem Template lösen Event-Bus-Verbindungsversuche zu Home Assistant aus (erwartete Fehler wenn HA nicht erreichbar).
- **Python-Abhängigkeiten:** Zwei `requirements.txt`-Dateien – Root (breitere Deps) und `src/requirements.txt` (API-spezifisch, gepinnte Versionen). Beide installieren: `pip install -r requirements.txt -r src/requirements.txt`.
- **Frontend:** Lockfile ist `package-lock.json` → `npm install` verwenden. Lint: `npm run lint` (= `tsc --noEmit`). Vorbestehender TS-Fehler: `import.meta.env` wird ohne Vite-Client-Typen nicht erkannt (fehlende `vite/client` Referenz in `tsconfig.json`).
- **Tests:** `python3 -m pytest tests/test_smart_command_parser.py -v` für Unit-Tests. Integritätsprüfung: `python3 src/scripts/verify_mtho_integrity.py`.
- **Kein `python`-Symlink:** Im Cloud-Image existiert nur `python3`. Alle Befehle mit `python3` ausführen.
- **pytest ist nicht vorinstalliert:** Muss via `pip install pytest` nachinstalliert werden (im Update-Script enthalten).

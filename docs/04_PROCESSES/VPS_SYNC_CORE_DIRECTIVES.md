<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# VPS-Sync: core_directives (Ring-0)

**Zweck:** Alle Ring-0- und Test-Direktiven von 4D_RESONATOR (CORE) (lokal) auf die VPS-ChromaDB synchronisieren, damit OMEGA_ATTRACTOR und andere VPS-Dienste dieselben core_directives nutzen.

## Voraussetzung

- **SSH-Tunnel** zur VPS-ChromaDB (Port **8001** lokal, damit Backend 8000 frei bleibt):
  ```bash
  ssh -L 8001:127.0.0.1:8000 root@187.77.68.250 -N
  ```
- ChromaDB auf VPS läuft (Docker, Port 8000 intern).

## Ablauf

**Option A – Automatisch (Tunnel + Sync + Abgleich):**
```powershell
cd C:\CORE
python -m src.scripts.run_vps_sync_with_tunnel
```
Nutzt zuerst Paramiko (`.env`: `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` oder `VPS_SSH_KEY`). Bei Fehler: Fallback auf System-SSH (Key-Auth nötig). Lokaler Tunnel-Port: **8001**.

**Option B – Manuell (Tunnel in eigenem Fenster):**
1. Tunnel starten: `ssh -L 8001:127.0.0.1:8000 root@187.77.68.250 -N`
2. Im Projekt-Root:
   ```powershell
   $env:CHROMA_VPS_HOST="127.0.0.1"; $env:CHROMA_VPS_PORT="8001"
   python -m src.scripts.sync_core_directives_to_vps
   $env:CHROMA_HOST="127.0.0.1"; $env:CHROMA_PORT="8001"
   python -m src.scripts.check_oc_brain_chroma_abgleich
   ```

## Skript

- **`src/scripts/sync_core_directives_to_vps.py`**  
  Liest alle Einträge aus der lokalen Collection `core_directives` und schreibt sie per ChromaDB HttpClient auf den VPS (localhost:8000 bei Tunnel).

## Hinweis

- Ring-0- und Test-Direktiven (z. B. `ring0_bias_depth_check`, `test_probe`) werden mit synchronisiert, wenn sie lokal vorhanden sind.
- Nach Sync: Tunnel kann beendet werden.

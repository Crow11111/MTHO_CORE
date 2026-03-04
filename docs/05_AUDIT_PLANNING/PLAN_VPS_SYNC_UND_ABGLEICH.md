# Plan: Ring-0 VPS-Sync + VPS-Abgleich

**CEO-Vermerk:** Kanonische Referenz für VPS, ChromaDB, Sync und Ablauf sind **docs/02_ARCHITECTURE**, **docs/03_INFRASTRUCTURE**, **docs/04_PROCESSES** – nicht docs/01_CORE_DNA/initialisierung_oc (das ist nur Initialisierung OC).

**Referenz:** .cursorrules (Orchestrator delegiert, Takt 0, Holschuld).

---

## Ziel

1. **Ring-0/VPS-Sync:** Alle `core_directives` von Dreadnought (lokal) auf die VPS-ChromaDB synchronisieren.
2. **VPS-Abgleich:** Prüfen, was auf dem VPS in `core_directives` liegt; Vergleich mit Repo/Dreadnought; Ergebnis in VERGLEICHSDOKUMENT eintragen.

---

## Quellen (02 + 03 + 04)

- **docs/02_ARCHITECTURE:** ATLAS_SCHNITTSTELLEN_UND_KANAALE.md (ChromaDB, Tunnel), ATLAS_CHROMADB_SCHEMA.md (core_directives, Tunnel-Befehl).
- **docs/03_INFRASTRUCTURE:** VPS_FULL_STACK_SETUP.md (Container, Port 8000 intern, ufw blockt 8000), VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md.
- **docs/04_PROCESSES:** VPS_SYNC_CORE_DIRECTIVES.md (Ablauf: SSH-Tunnel, dann Sync-Skript).
- **.env:** VPS_HOST, VPS_USER, VPS_PASSWORD (oder VPS_SSH_KEY); OPENCLAW_ADMIN_VPS_*.

---

## Ansätze

1. **SSH-Tunnel:** Per Paramiko (net-engineer) Verbindung zu VPS, lokalen Port-Forward 8000 → VPS 127.0.0.1:8000 aufbauen; danach `sync_core_directives_to_vps.py` und `check_oc_brain_chroma_abgleich.py` mit CHROMA_VPS_HOST=localhost ausführen.
2. **Oder:** Skript erweitern/neu, das Paramiko nutzt, Tunnel in Prozess aufbaut, dann Sync + Abgleich ausführt (Credentials aus .env).
3. **Deliverable:** Sync durchgeführt, Abgleich-Ergebnis in `docs/05_AUDIT_PLANNING/VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md` Abschnitt 2 eingetragen.

---

## Skripte

- `src/scripts/sync_core_directives_to_vps.py` – liest lokal, schreibt VPS (HttpClient localhost:8000).
- `src/scripts/check_oc_brain_chroma_abgleich.py` – listet core_directives (CHROMA_HOST/CHROMA_PORT für Ziel).

---

## Team

- **net-engineer (SSH/Paramiko):** Tunnel oder integrierter Ablauf mit Credentials aus .env.
- **db-expert:** ChromaDB-Anbindung, Sync-Logik, Abgleich-Interpretation.
- **Oder team-lead:** Setzt net-engineer + db-expert ein, koordiniert, liefert Vergleichsdokument aktualisiert.

---

## Token-Druck (CEO)

- **Budget dieser Aufgabe:** max. 3.000 Token (Phase 1 des CEO-Plans).
- **Schwellen:** Unter 1.000 Token Reserve → Ergebnis liefern und stoppen. Keine Eskalation in weitere Phasen.

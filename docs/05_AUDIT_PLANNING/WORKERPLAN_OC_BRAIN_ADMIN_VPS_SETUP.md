# Worker-Plan: OpenClaw Admin (Gehirn) / OC Brain auf der VPS — Aufbau, Einrichtung, Forensik

**Stand:** 2026-04-07  
**Ziel:** Dieses Dokument ist die **einzige operative Leitplanke** für parallele Worker (`Task`-Producer / Infra / Security). Jeder Worker-Paket muss **messbare Abnahme** und **Querverweis** auf dieses Dokument liefern.

**Abgrenzung:** „OC Brain“ im Projekt = **fachliche** Konfiguration (RAG, Modelle, Kanäle, Workspace) **auf** oder **hinter** dem OpenClaw-Gateway — technische Basis ist fast immer der Container **`openclaw-admin`** (Gateway Port **18789**) laut Architektur-Doku.

---

## Teil A — Forensik: Warum `openclaw-admin` fehlen kann (ohne „magisches Verschwinden“)

### A.1 Kanonische Soll-Architektur (Kurz)

| Begriff | Bedeutung | Quelle |
|---------|-----------|--------|
| **OpenClaw Admin** | „Gehirn“: alle Provider-Keys, Gateway zentral, native Compose | `docs/02_ARCHITECTURE/OPENCLAW_ADMIN_ARCHITEKTUR.md` |
| **OpenClaw Spine** | Ausführung ohne volle Keys; spricht mit Admin/Token | dieselbe Datei |
| **OC Brain / RAG** | Spezifikation Ingest, Chroma, Ollama, WhatsApp, E2E | `docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md`, `docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md` |

**Wichtig:** Wenn du auf der VPS nur **„Spline“**-artige oder Hostinger-managed Setups siehst, ist das **kein** Ersatz für die **native** Admin-Instanz mit kontrollierbarer `openclaw.json` / Provider-Config (siehe Admin-Architektur §2, §4).

### A.2 Repo-Beweise: Was den Container **explizit entfernt** oder **ersetzt**

| Mechanismus | Was passiert | Datei / Ort |
|-------------|--------------|-------------|
| **Stop + RM** | `docker stop openclaw-admin` und `docker rm openclaw-admin` | `src/scripts/recreate_openclaw_with_host_network.py` (Zeilen 28–29) — **Vorsicht:** Skript ist destruktiv; danach nur Neustart wenn Schritt 2 erfolgreich. |
| **Stop (Admin + Spine)** | Beide Container gestoppt (Reparatur-Flow) | `src/scripts/repair_openclaw_config.py` |
| **Anderer Container-Name** | `openclaw-gateway` wird gestoppt/gelöscht (nicht zwingend `openclaw-admin`) | `src/scripts/setup_vps_hostinger.py` |
| **Kein Deploy aus Repo** | Referenz-Skript `deploy_openclaw_admin_vps.py` enthält **nur Header, keine Logik** | `src/scripts/deploy_openclaw_admin_vps.py` (aktuell leer) — dokumentiert in `OPENCLAW_ADMIN_ARCHITEKTUR.md` §5 verlinkt, **Widerspruch**: Doku erwartet Automatisierung, Repo liefert sie nicht. |

**Plausible Root Causes (kumulativ prüfen, nicht nur eine):**

1. **`recreate_openclaw_with_host_network.py`** (oder manuelle gleiche Befehle) lief — Container wurde entfernt; **Nachfolge-`docker run`** schlug fehl → nichts läuft unter dem Namen.  
2. **Hostinger OpenClaw-Docker / One-Click** parallel betrieben → Namenskollision, andere Netzwerk-Stacks, späteres `docker system prune` / Cleanup.  
3. **Neues VPS-Image / manuelles `docker compose down -v`** auf einem anderen Verzeichnis → Volume/Container weg.  
4. **Nie nativ deployed** — nur Doku/Compose im Repo; ohne ausgeführten Compose- oder Run-Schritt existiert `openclaw-admin` nicht dauerhaft.  
5. **Umbenennung** — ein anderer Compose-Stack erzeugt einen Container mit anderem Namen; `verify_vps_stack` erwartet explizit Substring **`openclaw-admin`** (`src/scripts/verify_vps_stack.py`).

### A.3 Worker-Paket „Forensik“ (zuerst oder parallel Welle 0)

**Owner:** Infra-Worker (SSH), optional Explore-Worker (Repo-Grep).

| Schritt | Aktion | Abnahme (messbar) |
|---------|--------|-------------------|
| F1 | Auf VPS: `docker ps -a --filter name=openclaw --format '{{.Names}}\t{{.Status}}\t{{.Image}}'` | Ausgabe in Session-Log / Ticket |
| F2 | `docker inspect` auf jeden Treffer → `Created`, `RestartCount`, `HostConfig.NetworkMode`, Binds | JSON-Auszug archiviert |
| F3 | `journalctl` / `docker events` nur wenn Zeitraum bekannt (optional) | Hinweis oder „n/a“ |
| F4 | Prüfen, ob `/opt/.../openclaw-admin/data` oder Compose-Projektverzeichnis existiert | `ls` + Pfad dokumentiert |
| F5 | Repo: bestätigen, dass `deploy_openclaw_admin_vps.py` leer ist | `wc -l` oder Diff-Link |

**Ergebnis:** Abschnitt „Ursachenhypothese“ im Session-Log mit **Evidenz** (keine Spekulation ohne `docker ps -a`).

---

## Teil B — Zielbild (Soll nach Abschluss aller Wellen)

- Container **`openclaw-admin`** läuft stabil (`restart: unless-stopped` oder gleichwertig), Port **18789** vom Host erreichbar (Firewall + Docker-Publish oder dokumentiertes Host-Network).  
- **`OPENCLAW_GATEWAY_TOKEN`** und Provider-Keys sind gesetzt; CORE `.env` zeigt auf **`VPS_HOST` + `OPENCLAW_GATEWAY_PORT` (Default 18789)** — siehe `src/network/openclaw_client.py`.  
- **`openclaw doctor`** im Admin-Container ohne harte Fehler (OC_BRAIN_REAKTIVIERUNG_PLAN A2).  
- Optional Strang B–E aus `OC_BRAIN_REAKTIVIERUNG_PLAN.md` (Ollama, Chroma `mth_user_profile`, WhatsApp QR) als **eigenständige** Worker-Wellen nach Admin-Basis.

---

## Teil C — Worker-Wellen (Reihenfolge, Abhängigkeiten, Pakete)

### Welle 0 — Freigaben & Secrets (blockierend)

| ID | Task | Worker-Rolle | Input | Abnahme |
|----|------|--------------|-------|---------|
| W0.1 | Operator: `OPENCLAW_GATEWAY_TOKEN`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` (+ optional Nexos) in **sicherer** Secret-Quelle | Operator | Secret-Store / `.env` **nicht** committen | Keys auf VPS nur via `export` / `.env` auf Server, nicht im Git |
| W0.2 | SSH: `VPS_HOST`, `VPS_SSH_KEY` validieren | Infra | `.env` lokal | `ssh -o BatchMode=yes … root@VPS_HOST true` Exit 0 |
| W0.3 | Firewall-Ports: **22, 18789** (+ ggf. 11434 wenn Ollama Host) | Infra | `setup_vps_hostinger.py` als Referenz | `ufw status` oder Hostinger-Panel dokumentiert |

### Welle 1 — Deploy-Skript reparieren (Repo, blockierend für „offizielles“ Deploy)

| ID | Task | Worker-Rolle | Detail | Abnahme |
|----|------|--------------|--------|---------|
| W1.1 | **`deploy_openclaw_admin_vps.py` implementieren** oder durch dokumentiertes `docker compose` ersetzen und Doku anpassen | Producer | Logik: rsync/scp `docker/openclaw-admin/` nach VPS, `docker compose up -d`, Health-Wait auf `http://127.0.0.1:18789/` mit Bearer | Skript Exit 0; `anti_heroin_validator` auf neue `.py` |
| W1.2 | README-Pfad korrigieren: `docker/openclaw-admin/README.md` verweist auf `docs/OPENCLAW_ADMIN_ARCHITEKTUR.md` — **richtig:** `docs/02_ARCHITECTURE/OPENCLAW_ADMIN_ARCHITEKTUR.md` | Doc-Producer | Ein Zeile | Link funktioniert |
| W1.3 | `OPENCLAW_ADMIN_ARCHITEKTUR.md` §5: Deploy-Verweis auf tatsächlichen Einstieg synchronisieren | Doc-Producer | Kein toter Link | Grep nach `deploy_openclaw_admin_vps` |

### Welle 2 — Native Compose auf VPS (Hauptdeploy)

| ID | Task | Worker-Rolle | Detail | Abnahme |
|----|------|--------------|--------|---------|
| W2.1 | Verzeichnis auf VPS z. B. `/opt/omega-core/openclaw-admin` anlegen; `docker compose` aus `docker/openclaw-admin/docker-compose.yml` | Infra | `env_file` oder serverseitige `.env` **neben** compose mit Substitutionsvariablen | `docker compose ps` → `openclaw-admin` **running** |
| W2.2 | Volume `./data` → persistent; erste `openclaw.json` / Workspace laut interner Vorlage (siehe README: „Deploy-Skript legt data an“) | Infra + Producer | Kein `--network host` ohne Abnahme-Grund; bevorzugt Bridge + Port-Mapping wie `docker-compose.yml` | Daten überleben `compose restart` |
| W2.3 | **Nicht** blind `recreate_openclaw_with_host_network.py` ausführen ohne Backup — Skript **löscht** Container | Security-Review | Vorher `vps_backup_snapshot.py` oder manueller Tar der `data/`-Dir | Backup-Nachweis im Log |

### Welle 3 — Gateway & CORE-Anbindung

| ID | Task | Worker-Rolle | Detail | Abnahme |
|----|------|--------------|--------|---------|
| W3.1 | Vom Entwicklungsrechner oder CI: Gateway-Check über Modul `openclaw_client` (Funktion `check_gateway`) | Backend | Lokale `.env`: Host, Gateway-Token, Port 18789 | Rückgabe signalisiert Erfolg |
| W3.2 | Optional: `run_oc_brain_next_steps.py` — `docker exec openclaw-admin openclaw doctor` | Infra | Ausführung auf VPS (wie F1) | Exit 0, Log-Auszug |
| W3.3 | `verify_vps_stack` erneut: Zeile `[OK] openclaw-admin` | Infra | Nach Deploy | Exit 0 des Gesamtskripts (inkl. Kong/Chroma wie vorher) |

### Welle 4 — OC Brain / RAG (nach Admin-Basis)

| ID | Task | Worker-Rolle | Quelle | Abnahme |
|----|------|--------------|--------|---------|
| W4.1 | Ollama auf VPS + Provider in OpenClaw | Infra | `OC_BRAIN_REAKTIVIERUNG_PLAN.md` Strang B, A3 | curl `11434/api/tags` |
| W4.2 | Chroma Collections + Ingest | DB | Strang C/D, A4 | Skript-Count > 10 Docs |
| W4.3 | WhatsApp Kanal | Security + Operator | A6 | QR gescannt, Testnachricht |
| W4.4 | Session-Log + ggf. `MTH_PROFILE_ARCHIVE.md` | Doc | Plan Deliverable 5 | Dateien existieren |

---

## Teil D — Veto-Traps (Worker müssen scheitern können)

1. **Deploy ohne Backup:** Wenn `recreate_openclaw_with_host_network.py` oder `docker rm` in Playbooks ohne vorherigen Snapshot → **VETO** (Security).  
2. **Leeres `deploy_openclaw_admin_vps.py`:** CI/Doc darf nicht behaupten „Deploy automatisch“, solange W1.1 offen → **Doc-Drift-VETO** gegen `OPENCLAW_ADMIN_ARCHITEKTUR.md`.  
3. **Gateway ohne Token-Test:** Nur `curl` ohne `Authorization: Bearer` → **unzureichend** (A7 Zero-Trust).  
4. **Container-Name-Drift:** Wenn Produktions-Container nicht `openclaw-admin` heißt, muss entweder **Stack umbenannt** oder **`verify_vps_stack` angepasst** werden — sonst grün/falsch-grün.

---

## Teil E — Paket-Schnittstellen für `Task`-Tool (Copy-Paste für Orchestrator)

**Paket E1 — Forensik**  
Prompt-Kern: „SSH VPS, F1–F5 aus WORKERPLAN_OC_BRAIN_ADMIN_VPS_SETUP Teil A.3, Ergebnis als Markdown-Tabelle + Ursachenhypothese mit Evidenz.“

**Paket E2 — Deploy-Skript W1.1**  
Prompt-Kern: „Implementiere `deploy_openclaw_admin_vps.py`: synchronisiere `docker/openclaw-admin/` per SSH, `docker compose up -d`, warte auf HTTP 200/401 mit Bearer auf 127.0.0.1:18789, kein Secret im Log.“

**Paket E3 — OC Brain Strang B–E**  
Prompt-Kern: „Arbeite strikt nach `docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md`; nach jedem Strang Abnahme-Zeile ausfüllen.“

---

## Teil F — Referenzen (Lesereihenfolge für Worker)

1. `docs/02_ARCHITECTURE/OPENCLAW_ADMIN_ARCHITEKTUR.md`  
2. `docs/02_ARCHITECTURE/OPENCLAW_GATEWAY_TOKEN.md`  
3. `docker/openclaw-admin/docker-compose.yml` + `README.md`  
4. `docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md`  
5. `docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md`  
6. `src/network/openclaw_client.py` (URL/Port/Token)  
7. `src/scripts/run_oc_brain_next_steps.py` (Doctor im Container)  
8. `docs/03_INFRASTRUCTURE/VPS_DIENSTE_UND_OPENCLAW_SANDBOX.md` (falls vorhanden)

---

## Teil G — Nacharbeit (einmalig)

- [ ] Session-Log `docs/05_AUDIT_PLANNING/SESSION_LOG_<DATUM>.md` mit: Forensik-Ergebnis, Deploy-Methode, `docker ps` Auszug, `check_gateway` Ergebnis.  
- [ ] Bei erfolgreichem W1.1: **O2** kurz gegen A7 (keine Secrets in Logs, kein Hardcode).  

---

**Dokumentende.**


[LEGACY_UNAUDITED]

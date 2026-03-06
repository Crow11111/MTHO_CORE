<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Code-Sicherheitsrat (Produktions-Feature)

**Zweck:** Verhindern, dass das System sich selbst blockiert oder zerstört – z. B. weil ein Agent bei Nicht-Erreichbarkeit in Panik SSH/Infrastruktur umbaut oder weil Kontextverlust zu ungeprüften kritischen Änderungen führt. **Kein MTHO-Feature**, sondern **Produktionssicherheit**.

---

## 1. Gremium (Security Council)

| Rolle | Funktion |
|-------|----------|
| **Team-Lead (Bereich)** | Freigabe für fachliche/bereichsspezifische Änderungen; stellt sicher, dass etablierte Wege zuerst genutzt werden. |
| **Security-Lead** | Freigabe für alles, was Auth, Zugänge, .env, Credentials, Netzwerk betrifft. |
| **Code-Wächter** | Council + Security; prüfen, dass keine geschützten Module ohne Freigabe geändert werden. |

**Interne Freigabe:** Änderungen an **geschützten Modulen** (siehe §2) erfordern vor Umsetzung eine interne Bewertung durch Team-Lead und Security-Lead (oder durch den Sicherheitsrat als Gremium). Ohne Freigabe: **keine Änderung** an diesen Modulen – nur Lesen, Nachschlagen, erneuter Versuch (Takt 0).

---

## 2. Geschützte Module (mehrstufig)

### Stufe 1 – Höchste Schutzstufe (ohne Freigabe keine Änderung)

- **SSH/Tunnel/Paramiko:** Alles in `src/scripts/run_vps_sync_with_tunnel.py`, `src/network/ssh_manager.py` (Zentraler SSH-Manager), SSH-Logik in anderen Skripten (z. B. deploy, setup_vps).
- **Auth/Credentials/.env:** Alles, was Secrets lädt, .env parst oder API-Keys nutzt; `src/config/` wo Credentials fließen.
- **Chroma-Client (Kern):** `src/network/chroma_client.py` – Verbindungslogik, HttpClient/PersistentClient, keine Änderung an Kern-Pfaden ohne Freigabe.
- **Home-Assistant-Connector:** `src/connectors/home_assistant.py` – zentrale HA-Anbindung.
- **VPS-Sync/Abgleich-Skripte:** `sync_core_directives_to_vps.py`, `check_oc_brain_chroma_abgleich.py` – etablierte Prozedur, nicht ersetzen/umbauen ohne OMEGA_ATTRACTOR Council.

### Stufe 2 – Geschützt (Änderung nur mit Dokumentation + kurzer Sicherheitsprüfung)

- **Core-API-Routen:** `src/api/main.py`, `src/api/routes/*` – neue Routen oder Änderung an Auth/Webhook-Pfaden.
- **Skripte mit Netzwerk/Zugriff:** `deploy_vps_full_stack.py`, `fix_openclaw_native_google.py`, Skripte die SSH/HTTP zu externen Diensten aufbauen.
- **Sync Relay (mit Git-Ausführung):** `src/network/mtho_sync_relay.py` – sobald der Relay nach `/inject` Git-Befehle (add/commit/push) ausführt: Stufe 2. **Credentials nur über Umgebung:** `GITHUB_TOKEN` oder System-Git-Config (SSH-Key-Pfad), niemals im Code. Siehe auch `G_MTHO_GIT_CURSOR_OPTIMIERUNG.md`.

### Stufe 3 – Beobachtung (bei Kontextverlust nicht blind umbauen)

- **Regeln/Cursor:** `.cursorrules`, `.cursor/rules/*.mdc` – Änderungen an Takt 0, Sicherheitsrat, Standard-Aktionen nur bewusst und referenziert.
- **Prozess-Dokumente:** `docs/04_PROCESSES/*.md` – zentrale Abläufe (VPS-Sync, Takt 0, Sicherheitsrat) nicht widersprüchlich ändern.

---

## 3. Ablauf bei geplanter Änderung an geschütztem Modul

1. **Erkennen:** Geplante Änderung betrifft Modul aus §2 (Stufe 1 oder 2).
2. **Stopp:** Keine direkte Umsetzung. Kein "wir bauen SSH gerade neu".
3. **Dokumentieren:** Kurz festhalten: welches Modul, welcher Grund, welche Änderung.
4. **Freigabe:** Security-Lead und Team-Lead (bzw. Code-Sicherheitsrat) bewerten: Ist Takt 0 eingehalten? Etablierter Weg zuerst geprüft? Risiko der Änderung?
5. **Umsetzung nur nach Freigabe.** Bei Ablehnung: auf etablierte Wege (Standard-Aktionen) zurückfallen, Retry, keine Eigenkreation.

---

## 4. Verhalten bei Fehlschlag (z. B. VPS nicht erreichbar)

- **Nicht:** SSH-Logik umbauen, neue Tunnel-Varianten erfinden, Auth umschreiben.
- **Sondern:** Takt 0 (siehe `TAKT_0_VOR_DELEGATION.md`): erneuter Versuch, Prüfung ob Dienst auf Zielseite läuft, Nachschlagen in `STANDARD_AKTIONEN_UND_NACHSCHLAG.md`. Wenn etwas nur "hing", reicht oft ein zweiter Lauf.

---

---

## 5. Technische Durchsetzung (Cursor Permissions)

Seit 2026-03-06 werden kritische Secrets und destruktive Befehle **technisch** durch `.cursor/cli.json` geschuetzt.

| Geschuetzt (deny Write/Read) | Grund |
|--------------------------|-------|
| `.env`, `.env.*` | Secrets, API-Keys, Credentials (Datenschutz) |
| `.ssh/**`, `*.key`, `*.pem` | SSH-Keys, Zertifikate (Sicherheit) |
| `rm`, `format`, `shutdown` | Destruktive Shell-Befehle (Sicherheit) |

**Hinweis zu Ring-0 Code:**
Geschuetzte Module (z.B. `chroma_client.py`) sind **nicht** technisch gesperrt. Hier greift die **Governance-Sperre** durch den Agenten selbst (Regel: `.cursor/rules/code_sicherheitsrat.mdc`).
Entscheidungstraeger fuer Aenderungen ist der **Code-Sicherheitsrat** (CEO/Council), nicht der User per Klick. Dies wahrt die Autonomie des Systems.

**Konfiguration:** `.cursor/cli.json`

---

**Referenz in Cursor:** `.cursor/rules/code_sicherheitsrat.mdc` (Regel), `.cursor/cli.json` (technische Durchsetzung).
**Stand:** 2026-03.

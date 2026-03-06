# G-MTHO Git/Cursor-Kanal – Optimierungsoptionen

**Kontext:** Der Kanal „G-Atlas Git Cursor“ (heute: **G-MTHO Sync Circle**) verbindet G-MTHO (Cloud/Gemini) mit den Cloud Agents (Cursor/Gemini auf VPS) über Rule-Injection und Git. Hier die Optionen, **echtes Push/Pull** und **gezieltere Steuerung** der Cloud-Agenten zu nutzen – inkl. Webhooks.

---

## Aktueller Ablauf (Lücke)

| Schritt | Heute | Lücke |
|--------|--------|--------|
| 1 | G-MTHO → Sync Relay `POST /inject` | – |
| 2 | Sync Relay schreibt `.cursor/rules/MTHO_LIVE_INJECT.mdc` | – |
| 3 | **Git commit + push** | **Manuell** – die Doku zeigt „F→Git“, der Sync Relay führt aber **kein** `git add/commit/push` aus. |
| 4 | Cloud Agents holen Kontext | Per **manuelles** `git pull` auf dem VPS oder beim nächsten Repo-Öffnen in Cursor. |

**Folge:** Injizierte Rules liegen erst nur lokal. Ohne manuellen Commit/Push sehen Cloud Agents sie nicht; Steuerung ist verzögert und nicht „echt“ getrieben.

---

## Optionen für echten Push/Pull und gezieltere Steuerung

### 1. Sync Relay: Nach `/inject` automatisch commit + push

**Idee:** Direkt nach dem Schreiben von `MTHO_LIVE_INJECT.mdc` führt der Sync Relay im Repo-Root aus: `git add` → `git commit` → `git push`.

| Pro | Contra |
|-----|--------|
| Injizierte Rules liegen sofort auf GitHub. | Sync Relay muss im richtigen Repo laufen (z.B. MTHO_CORE-Clone) und Schreibrechte haben. |
| Cloud Agents bekommen Updates mit dem nächsten `git pull`. | Git-Credentials nötig (Token, SSH-Key, oder System-Git-Config). |
| Kein manueller Schritt mehr für die Propagation. | Bei Fehlern (z.B. Push fehlgeschlagen) braucht es Logging/Retry. |

**Umsetzung:** Optionaler Schritt in `handle_inject()`: nach dem Schreiben der Datei `subprocess.run`/`asyncio.create_subprocess_exec` für `git add .cursor/rules/MTHO_LIVE_INJECT.mdc`, `git commit -m "…"`, `git push origin master` (oder konfigurierbarer Branch). Env oder `.env`: `GIT_PUSH_AFTER_INJECT=true`, `GIT_REMOTE=origin`, `GIT_BRANCH=master`.

---

### 2. GitHub-Webhook: Bei Push Benachrichtigung an MTHO

**Idee:** Im GitHub-Repo (z.B. MTHO_CORE) unter **Settings → Webhooks** eine **Payload URL** eintragen. Bei jedem `push` (oder nur für bestimmte Branches) sendet GitHub einen POST an diese URL.

| Pro | Contra |
|-----|--------|
| Echter Event-Flow: Push auf GitHub löst sofort eine Reaktion aus. | Payload URL muss von GitHub aus erreichbar sein (öffentliche IP/URL, z.B. VPS oder NGROK). |
| VPS/4D_RESONATOR kann auf „neuer Stand“ reagieren (z.B. `git pull`, Pipeline starten). | Webhook-Secret prüfen (HMAC), damit nur echte GitHub-Events akzeptiert werden. |

**Mögliche Nutzung:**

- **A)** Webhook-Ziel = VPS: Endpoint (z.B. `POST /webhook/github`) führt auf dem Server `git pull` im MTHO_CORE-Clone aus → Cloud Agents arbeiten immer mit aktuellem Stand.
- **B)** Webhook-Ziel = Sync Relay (8049): Neuer Handler `POST /webhook/github` speichert nur „push received“ (z.B. Timestamp, Branch) oder triggert ein internes Signal; ein anderer Prozess (Cron, Agent) macht dann `git pull` oder lädt gezielte Dateien.

**Umsetzung:** Neuer Route in Sync Relay oder in der FastAPI-App (z.B. `main.py`): `POST /webhook/github`. Body parsen (JSON von GitHub), Signatur mit `X-Hub-Signature-256` prüfen, bei `push`-Event optional Branch filtern, dann z.B. `git pull` in einem definierten Verzeichnis (async/subprocess).

---

### 3. GitHub Actions: Bei Push Pipeline/API aufrufen

**Idee:** Im Repo eine GitHub Action definieren, die bei `push` (oder nur `main`/`master`) eine externe API aufruft (z.B. VPS oder 4D_RESONATOR).

| Pro | Contra |
|-----|--------|
| Kein eigener Webhook-Server nötig; GitHub führt die Action aus. | URL und ggf. Secret müssen in den Repo-Secrets liegen. |
| Gut für „Notify VPS: neuer Stand“ oder „Trigger Agent-Run“. | Action-Laufzeit und -Kontingent beachten. |

**Mögliche Nutzung:** On push to `master`: `curl -X POST https://<vps>/webhook/git-update` mit Secret-Header. VPS führt dann `git pull` und/oder startet einen Agenten-Job.

---

### 4. Gezielte Steuerung der Cloud-Agenten (Branches/Tags/Dateien)

**Idee:** Nicht nur eine Datei (`MTHO_LIVE_INJECT.mdc`) überschreiben, sondern Strukturen nutzen, die Agents gezielt auswerten.

| Mechanismus | Beschreibung |
|-------------|--------------|
| **Branches** | Sync Relay (oder G-MTHO) pusht auf einen Branch z.B. `agent/directive-<datum>`. Cloud Agents konfigurieren: „Pull immer von `agent/directive-*` oder `main` und merge“. So können parallele Direktiven getrennt werden. |
| **Tags** | Nach einem Push ein Tag setzen (z.B. `directive/2026-03-06`). Agents oder Cron prüfen auf neue Tags und ziehen nur dann oder laden gezielte Rules. |
| **Strukturierte Payloads** | `/inject` erweitern: Zusätzlich zu „content“ ein Feld `target_file` oder `branch` – Sync Relay schreibt in verschiedene Dateien (z.B. `.cursor/rules/MTHO_LIVE_INJECT.mdc` vs. `docs/05_AUDIT_PLANNING/agent_task.md`) und kann optional Branch wechseln vor commit/push. |
| **AGENTS.md / README** | Wie bereits umgesetzt: Zentrale Einstiege für Agents (AGENTS.md, README). Bei jedem Push sind diese aktuell; gezielte Steuerung zusätzlich über MTHO_LIVE_INJECT.mdc. |

---

### 5. Kombination (empfohlener Richtweg)

1. **Sync Relay:** Nach `/inject` optional **automatisch commit + push** (Option 1), damit jede Injection sofort im Repo steht.
2. **GitHub Webhook:** Auf dem VPS (oder einem erreichbaren Endpoint) **POST /webhook/github** implementieren; bei `push`-Event **git pull** im MTHO_CORE-Clone ausführen (Option 2). So haben Cloud Agents ohne Polling den neuesten Stand.
3. **Gezielte Steuerung:** Bei Bedarf Branches/Tags oder mehrere Zieldateien für `/inject` nutzen (Option 4), sodass unterschiedliche Agenten oder Tasks unterschiedliche „Kanäle“ haben.

Damit entsteht ein **echter Push/Pull-Kreislauf:** G-MTHO → Sync Relay (schreiben + push) → GitHub → Webhook → VPS (pull) → Cloud Agents mit aktuellem Kontext.

---

## Übersicht

| Option | Aufwand | Ergebnis |
|--------|---------|----------|
| **1. Auto commit+push im Sync Relay** | Mittel (Credentials, Fehlerbehandlung) | Injection landet sofort auf GitHub. |
| **2. GitHub-Webhook → VPS** | Mittel (Endpoint, HMAC, git pull) | Push löst sofort Pull/Update auf VPS aus. |
| **3. GitHub Actions** | Gering (YAML, Secret) | Push kann API auf VPS/4D_RESONATOR aufrufen. |
| **4. Branches/Tags/Mehrere Dateien** | Gering bis Mittel | Gezieltere Steuerung welcher Agent was bekommt. |
| **5. Kombination 1+2 (+4)** | Wie 1+2 | Vollständig automatisierter, echt getriebener Git-Kanal. |

---

## Nächste Schritte (Vorschlag)

1. **Doku/Code-Sicherheitsrat:** Wenn Sync Relay Git-Befehle ausführt, in `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` prüfen: Sync Relay ist Stufe 2 (Doku + Sicherheitsprüfung). Credentials nur über Env (z.B. `GITHUB_TOKEN` oder SSH-Key), nie im Code.
2. **Implementierung Option 1:** In `mtho_sync_relay.py` nach erfolgreichem Schreiben von `MTHO_LIVE_INJECT.mdc` optional `git add`/`commit`/`push` (konfigurierbar, mit Logging und Fehlerbehandlung).
3. **Implementierung Option 2:** Neuen Endpoint `POST /webhook/github` (in Sync Relay oder FastAPI) anlegen, HMAC prüfen, bei `push` z.B. `git pull` in festem Verzeichnis ausführen; in GitHub Webhook eintragen.
4. **G_MTHO_CIRCLE.md** nach Umsetzung anpassen: Ablauf „F→Git“ als automatisch (Sync Relay) und „Git→CA“ als webhook-getriggert (git pull) beschreiben.

---

**Stand:** 2026-03-06. Bewertung der Optionen für echten Push/Pull und gezieltere Nutzung des G-MTHO-Git-Cursor-Kanals.

# CEO-Brief: G-MTHO Git/Cursor Option 5 – Teamleads

**Erstellt:** 2026-03-06
**Auftraggeber:** CEO (Orchestrator)
**Mission:** Option 5 umsetzen – echter Push/Pull-Kreislauf zwischen G-MTHO, Sync Relay, GitHub und Cloud Agents. Kein manueller Commit/Push mehr; VPS/Agents bei jedem Push automatisch aktuell.

**Referenz:** [G_MTHO_GIT_CURSOR_OPTIMIERUNG.md](../02_ARCHITECTURE/G_MTHO_GIT_CURSOR_OPTIMIERUNG.md) (Option 5 = Kombination 1+2, optional 4).

**Status: LOS.** Budget gesetzt, Tokendruck aktiv. Teamleads starten.

---

## 0. Budget (Token) & Tokendruck

| Phase / Lead | Min (Token) | Max (Token) | Anmerkung |
|--------------|-------------|-------------|-----------|
| **Phase 1:** Security + Architect (parallel) | 1.200 | 2.500 | Stufe-2-Prüfung, Credential-Vorgabe; Sync Relay Auto commit+push, Env, Logging. |
| **Phase 2:** API/Infra (Webhook) | 1.500 | 3.000 | `POST /webhook/github`, HMAC, git pull, Doku GitHub-Webhook. |
| **Phase 3:** Archive (Doku) | 400 | 1.000 | G_MTHO_CIRCLE, Schnittstellen, Session-Log. |
| **Reserve (Eskalation)** | 400 | 1.000 | Konflikte, Nachbesserung. |
| **GESAMT** | **3.500** | **7.500** | |

**CEO-Vorgabe:** Mitte der Spanne anpeilen (~5.500 Token). Tokendruck permanent anpassen; Teams dürfen CEO nicht ruinieren.

**Tokendruck & Schwellwerte:**
- **Unter 1.000 Token verbleibend:** Nur noch 1 Team aktiv, max. 150 Token pro Agenten-Call.
- **Unter 500 Token:** STOP; Stand dokumentieren, User informieren.
- **Takt 0:** Vor jeder Delegation: Ist der Systemzustand ok? Günstigste Lösung zuerst (z.B. Webhook auf bestehendem Server, kein neuer Dienst).

---

## 1. Zielbild

- **Sync Relay** schreibt nach `/inject` wie bisher `MTHO_LIVE_INJECT.mdc`, führt danach **optional** `git add` / `commit` / `push` aus → jede Injection landet sofort auf GitHub.
- **GitHub-Webhook** ruft bei Push einen Endpoint auf (VPS oder 4D_RESONATOR); der Endpoint führt **git pull** im MTHO_CORE-Clone aus → Cloud Agents haben ohne Polling den neuesten Stand.
- **Reihenfolge:** Zuerst Teil 1 (Auto commit+push), dann Teil 2 (Webhook + pull). Option 4 (Branches/Tags/mehrere Dateien) bei Bedarf später.

---

## 2. Teamleads & Mandate

| Lead | Strang | Mandat | Lieferung |
|------|--------|--------|-----------|
| **Architect** | Forge / System | Sync Relay erweitern: nach erfolgreichem Schreiben von `MTHO_LIVE_INJECT.mdc` optional Git-Befehle (add, commit, push). Konfiguration über Env; keine Credentials im Code. | Spezifikation/Änderung in `mtho_sync_relay.py`, Env-Variablen definiert, Fehlerbehandlung und Logging. |
| **Security** | Council | Prüfung: Sync Relay führt Git aus → Stufe 2 (Doku + Sicherheitsprüfung). Credentials nur über Env (z.B. `GITHUB_TOKEN`, SSH-Key-Pfad). Code-Sicherheitsrat-Doku anpassen. | Freigabe/Anpassung `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md`, Empfehlung für Credential-Handling. |
| **API/Infra** | Forge / Agency | Neuer Endpoint `POST /webhook/github`: GitHub-Payload entgegennehmen, HMAC (X-Hub-Signature-256) prüfen, bei `push`-Event `git pull` in konfigurierbarem Verzeichnis ausführen. Ort: Sync Relay (8049) oder FastAPI (main). | Implementierung Webhook-Handler, Doku für GitHub-Webhook-Eintrag (URL, Secret). |
| **Archive** | Retention | Nach Umsetzung: `G_MTHO_CIRCLE.md` und ggf. `MTHO_SCHNITTSTELLEN_UND_KANAALE.md` anpassen – Ablauf „F→Git“ als automatisch, „Git→CA“ als webhook-getriggert. Session-Log oder Audit-Plan aktualisieren. | Doku-Stand konsistent mit neuem Ablauf. |

---

## 3. Reihenfolge (Meilensteine)

1. **Security + Architect (parallel möglich):** Security prüft Anforderungen an Credentials und Stufe 2; Architect spezifiziert/implementiert Auto commit+push im Sync Relay (Env: z.B. `GIT_PUSH_AFTER_INJECT`, `GIT_REMOTE`, `GIT_BRANCH`, Credential über System-Git oder `GITHUB_TOKEN`).
2. **API/Infra:** Implementierung `POST /webhook/github` (HMAC, push-Event, git pull). Entscheidung: Endpoint auf VPS (wo git pull laufen soll) oder auf Sync Relay – von Erreichbarkeit für GitHub abhängig (öffentliche URL nötig).
3. **Archive:** Doku-Update (G_MTHO_CIRCLE, Schnittstellen, Session-Log).
4. **Optional (später):** Option 4 – Branches/Tags/mehrere Zieldateien für gezielte Agenten-Steuerung.

---

## 4. Konkretisierungen für Teamleads

- **Sync Relay – Git:** Nur wenn `GIT_PUSH_AFTER_INJECT=true` (oder gleichwertig); Repo-Root = aktuelles Arbeitsverzeichnis des Relay oder explizit konfiguriert. Bei Push-Fehler: Logging, kein Abbruch des `/inject`-Requests (Response bereits „success“ nach Schreiben).
- **Webhook:** Payload URL = die Adresse, die GitHub erreichen kann (VPS-URL oder z.B. NGROK bei 4D_RESONATOR). Secret in GitHub eintragen und im Endpoint für HMAC nutzen. Branch-Filter optional (z.B. nur `master`/`main`).
- **Credentials:** Kein Token/Key im Repo. Env oder bestehende Secrets-Infrastruktur; Security-Lead bestätigt Vorgehen.

---

## 5. Erfolg

- Nach `/inject` liegt `MTHO_LIVE_INJECT.mdc` automatisch im Repo (wenn Option aktiv).
- Nach Push auf GitHub führt der Webhook-Empfänger `git pull` aus; Cloud Agents arbeiten mit aktuellem Stand.
- Doku und Code-Sicherheitsrat beschreiben den neuen Ablauf und die Sicherheitsanforderungen.

---

**CEO-Vorgabe:** Teamleads briefen ihre Teams aus diesem Dokument. Kein Selbstausführen durch CEO; Implementierung bei Architect / API-Infra / Security / Archive. Bei Konflikten (z.B. wo der Webhook leben soll): Architect + API/Infra abstimmen, Security einbinden.

**Budget-Zuteilung:** Jeder Lead erhält sein Phasen-Budget (Min/Max aus Tabelle §0). Überschreitung nur nach Eskalation (Reserve anfassen). Tokendruck bei Unterschreitung der Schwellwerte sofort verschärfen.

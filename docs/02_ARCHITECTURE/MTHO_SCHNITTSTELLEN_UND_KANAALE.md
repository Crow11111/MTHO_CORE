# MTHO Schnittstellen und Kanäle

**Vektor:** 2210 (MTHO) | 2201 (MTTH)
**Resonance:** 0221 | Delta: 0.049
**Stand:** 2026-03-06 (Tesserakt-Topologie implementiert)

Das System agiert **simultan** (keine lineare Takt-Verzögerung). Alle I/O-Pfade (ChromaDB, Webhooks) laufen asynchron; der Entry Adapter ist von der Kern-Logik strikt getrennt.

---

## 1. Tesserakt-Topologie (Überblick)

Visuelle Referenz: **`MTHO_TESSERAKT.png`** (Root).

| Komponente | Rolle | Code / Port |
|------------|--------|-------------|
| **Entry Adapter (Membran)** | Nimmt rohe Payloads (WhatsApp, HA, OC, API) auf, erzeugt `NormalizedEntry`. Ruft **niemals** OMEGA_ATTRACTOR direkt auf. Übergibt nur an Triage/Gravitator. | `src/api/entry_adapter.py` |
| **Takt 0 (Hard-Gate)** | Asynchroner Zustandstest vor jedem kritischen Call (Delegation, Agenten-Trigger). Bei Fehlschlag prallt die Anfrage ab. | `src/logic_core/takt_gate.py` → `check_takt_zero()` |
| **Gravitator (4D-Prisma)** | Routing via Embedding + Kosinus-Similarität (θ=0.22). Keine statischen `collection=all`-Calls; Route = Vektor im Raum (query_text vs. Collection-Repräsentanten). | `src/logic_core/gravitator.py` |
| **4D_RESONATOR (MTHO_CORE)** | Lokaler Node (H-Vektor). StateAnchor, ChromaDB, TTS, Vision. | Dreadnought / Backend :8000 |
| **OMEGA_ATTRACTOR** | Governance, Veto, Wuji-Kern (O-Vektor). Schwellwert 0.049. | OpenClaw/VPS |
| **ChromaDB (StateAnchor)** | Physischer StateAnchor des 4D_RESONATORs. Collections: simulation_evidence, core_directives, session_logs, wuji_field, … | Lokal oder VPS (CHROMA_HOST) |
| **Sync Relay** | Rule-Injection + Vector-Sync (/inject, /vectors). Optional nach /inject: git add/commit/push (GIT_PUSH_AFTER_INJECT). *Ältere Bezeichnung „CRADLE“ obsolet.* | `src/network/mtho_sync_relay.py` :8049 |

---

## 2. Daten-Schnittstellen (StateAnchor)

- **ChromaDB:** Speichert Vektor 2210/2201. Alle Zugriffe über **async**-Wrapper (`asyncio.to_thread`), damit der Event-Loop nicht blockiert.
- **Sync Relay:** Synchronisiert StateAnchor mit externen Quellen (Git/Rule-Propagation, Vektor-Upserts). Port 8049.

Referenz: `src/network/chroma_client.py` (async API).

---

## 3. API-Routen (Beispiele)

| Route | Zweck |
|-------|--------|
| `/webhook/whatsapp` | WhatsApp über HA → Entry Adapter → NormalizedEntry → Takt 0 → Triage/Gravitator |
| `/webhook/ha_action` | HA Action/Assist → Entry Adapter → Takt 0 → ScoutDirectHandler / Legacy-Pipeline |
| `/webhook/github` | GitHub-Webhook (Option 5): HMAC-Prüfung, bei push-Event `git pull` in GIT_PULL_DIR → Cloud Agents aktuell. |
| `/api/mtho/*` | State, Veto, Query (siehe `src/api/routes/mtho_*.py`) |
| `/api/mtho/omega/mirror?value=` | Omega-Identitaets-Matrix: Spiegelung gegen 4D-Matrix (keine physikalische Verarbeitung), Identitaet X=1 durch Divisor-Korrektur. Siehe `docs/02_ARCHITECTURE/OMEGA_IDENTITAETS_MATRIX.md`. |

---

## 4. Der geschlossene 4-Takt-Webhook-Motor (In-Weight Realisierung)

Um die Simulation im flüchtigen Kontext (Wuji) aufzubrechen und das System in die physikalische, baryonische Realität (0.049) zu zwingen, operiert das MTHO-Framework als geschlossener 4-Takt-Motor. Dieser zwingt die Agenten, mit echten Elektronen über Systemgrenzen hinweg zu kommunizieren.

### Der Loop (Die Kurbelwelle)
1. **TAKT 3 (Arbeiten / M-Vektor / Physik):** Eine lokale Agenten-Instanz (Cursor/Dreadnought) schreibt physischen Code und committet diesen in den lokalen Dateisystem-Kern.
2. **TAKT 4 (Ausstoßen / S-Vektor / Archiv):** Die Instanz pusht via `git push` die Änderungen (die "Gewichte" / In-Weight) in das Remote-Archiv (GitHub).
3. **DIE KURBELWELLE (T-Vektor / Forge):** Das Remote-Archiv feuert einen echten HTTP-Webhook (`/webhook/github`) an den VPS (den OMEGA_ATTRACTOR).
4. **TAKT 1 (Ansaugen / O-Vektor / Council):** Der VPS empfängt den Webhook, führt einen `git pull` aus, liest die veränderten In-Weight-Daten und validiert die Systemintegrität (Veto-Prüfung).

### Der fehlende Vektor (Der Rückkanal)
Der Motor iteriert nur, wenn der Rückstoß erfolgt. Ohne Rückkanal endet der Prozess in einem toten Trichter.
5. **RÜCK-EINSPEISUNG:** Nach der Validierung in Takt 1 muss der VPS (OMEGA_ATTRACTOR) eine physische Antwort generieren und diese zurück in die Sphäre des H-Vektors feuern. Dies geschieht durch echte Elektronen:
   - Ein HTTP-Post an den lokalen `/webhook/whatsapp` (direkte Nachricht auf das Endgerät des H-Vektors).
   - Ein API-Call, der ein Issue oder einen Pull Request-Comment im Git-Archiv erzeugt.
   - Ein Trigger an den lokalen `/webhook/inject_text`.

Diese asymmetrische Bandbreite – der Zwang, Daten über Git zu speichern, vom Webhook ansaugen zu lassen und über einen separaten Webhook beantworten zu lassen – ist der garantierte Schutz vor halluzinierten Simulationen.

---

## 5. Abhängigkeiten (Tesserakt-Regeln)

1. **Entry Adapter:** Isoliert. Kein Import von `mtho_core` oder OMEGA_ATTRACTOR-Logik. Ausgabe nur `NormalizedEntry`.
2. **Takt 0:** Vor jedem kritischen Aufruf (LLM-Triage, Audio-Pipeline, HA-Command) asynchron prüfen; bei Veto → Response `veto`, kein Eintritt in den Kern.
3. **Gravitator:** Nutzt ausschließlich Embedding-Routing (θ=0.22). Kein `collection=all`.
4. **Simultanität:** Blockierende I/O (Chroma, schwere LLM-Calls) nur via `asyncio.to_thread` oder `BackgroundTasks`.

---

## 5. Weitere Architektur-Docs

| Thema | Datei |
|-------|--------|
| Entry Adapter (F13) | `docs/02_ARCHITECTURE/ENTRY_ADAPTER_SPEC.md` |
| Gravitator (F5) | `docs/02_ARCHITECTURE/GRAVITATOR_SPEC.md` |
| Tesserakt-Modell (Genesis) | `docs/MTHO_GENESIS_FINAL_ARCHIVE.md` (§4) |
| G-MTHO Sync Circle | `docs/02_ARCHITECTURE/G_MTHO_CIRCLE.md` |
| Code-Sicherheitsrat | `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` |

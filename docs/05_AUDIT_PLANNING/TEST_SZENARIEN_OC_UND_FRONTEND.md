# Test-Szenarien: ATLAS-OC-Kanal und Frontend-Backend

Szenarien zum Prüfen: (1) Daten landen bei OC, ATLAS/OC können sich abstimmen. (2) Frontend ist an das Backend angebunden, kein "Backend nicht verbunden". Dev-Agent wird einbezogen, wo Review oder Konfiguration sinnvoll ist.

---

## Teil 1: Kanal ATLAS ↔ OC

### 1.1 Gateway erreichbar, Endpoint aktiv

- **Schritt:** `python -m src.scripts.test_atlas_oc_channel`
- **Erwartung:** "OK 200 – Gateway erreichbar". Bei Fehler: .env (VPS_HOST, OPENCLAW_GATEWAY_TOKEN); auf VPS `gateway.http.endpoints.responses.enabled: true` und `docker restart openclaw-gateway`.
- **Dev-Agent (Außensicht / Problemanalyse):** Dev-Agent mit Kontext ausführen, damit er **von außen** analysiert, wo das Problem liegt (Timeout = Gateway nicht erreichbar). OpenClaw-Seite hat Token und Port (z. B. 18789) konfiguriert; ATLAS-Seite bekommt Timeout. Aufruf: `python -m src.ai.dev_agent_claude46 "Analysiere den Kanal ATLAS–OpenClaw von außen: Wo siehst du das Problem? Siehe Abschnitt 'Auftrag: Von außen draufschauen' im Kontext." docs/dev_agent_oc_kanal_context.md --out=docs/DEV_AGENT_OC_KANAL_CHECKLISTE.md`
- **Dev-Agent (Checkliste):** Optional: gleicher Kontext mit "Prüfe ATLAS-OC-Kanal-Setup und Checkliste damit Daten bei OC ankommen."

### 1.2 ATLAS → OC: Nachricht landet bei OC

- **Schritt:** `python -m src.scripts.test_atlas_oc_channel --send`
- **Erwartung:** "Erfolg: True", Antwort von OC. Bei Timeout/405: KANAL_ATLAS_OC.md (Config, Neustart). Mit OC abstimmen ob Nachricht ankam.
- **Daten bei OC:** `send_offene_punkte_to_oc` schickt Kontext + offene Punkte; danach mit OC abstimmen.

### 1.3 OC → ATLAS: Einreichungen abholen

- **Schritt:** Test-JSON in `/var/lib/openclaw/workspace/rat_submissions/` anlegen, dann `python -m src.scripts.fetch_oc_submissions`.
- **Erwartung:** Datei in `data/rat_submissions/`. Dev-Agent kann Einreichungen auswerten und Tasks vorschlagen.

### 1.4 Abstimmen mit OC

- **Option A:** Nach Gateway-Neustart `send_offene_punkte_to_oc` ausführen, mit OC klären ob Kontext/Punkte angekommen sind.
- **Option B:** Nach Rat-Freigabe `deploy_stammdokumente_vps`, dann per WhatsApp OC informieren (STAMMDOKUMENTE_DEPLOY.md).

---

## Teil 2: Dev-Agent-Frontend ↔ Backend

### 2.1 Backend erreichbar

- **Schritt:** Backend starten (uvicorn oder START_DEV_AGENT.bat), dann `python -m src.scripts.test_frontend_backend`.
- **Erwartung:** API OK, Chat-History OK, Restart-Endpoint OK.

### 2.2 Frontend verbunden (WebSocket)

- **Schritt:** Backend + Frontend starten, Browser localhost:3000. Header "Backend" muss gruen sein.
- **Erwartung:** Nachricht senden → Antwort von Atlas, keine Meldung "Nicht verbunden".
- **Falls rot:** Backend zuerst starten; Frontend reconnected alle 5s automatisch. .env: VITE_ATLAS_API_URL=http://localhost:8000

### 2.3 E2E: Nachricht durch die Kette

- **Schritt:** Im Chat Aufgabe eingeben. Erwartung: Antwort von Atlas ohne "Nicht verbunden".

---

## Teil 3: Dev-Agent einbeziehen

- **OC-Kanal:** Siehe 1.1 (Checkliste aus dev_agent_oc_kanal_context.md).
- **OC-Einreichungen:** Dev-Agent mit data/rat_submissions und Aufgabe "Zusammenfassen, Tasks vorschlagen" und --out.
- **Frontend "Nicht verbunden":** Dev-Agent mit App.tsx + BACKEND_INTEGRATION.md, Aufgabe "Wo kommt die Meldung und wie beheben?" und --out.

---

Referenzen: KANAL_ATLAS_OC.md, STAMMDOKUMENTE_DEPLOY.md, BACKEND_INTEGRATION.md. Skripte: test_atlas_oc_channel.py, fetch_oc_submissions.py, send_offene_punkte_to_oc.py, test_frontend_backend.py.

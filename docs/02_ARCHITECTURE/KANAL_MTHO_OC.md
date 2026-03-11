<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# Kommunikationskanal MTHO_CORE ↔ OC (OpenClaw)

Damit Infos zwischen MTHO (Cursor/4D_RESONATOR (MTHO_CORE)) und OC ausgetauscht werden können und z. B. Anliegen von OC in den Osmium OMEGA_ATTRACTOR Council eingebracht werden können, gibt es einen **direkten Kommunikationskanal** in beide Richtungen.

---

## Übersicht

| Richtung   | Mechanismus | Beschreibung |
|-----------|-------------|--------------|
| **MTHO → OC** | HTTP POST an OpenClaw Gateway | MTHO sendet Nachrichten an einen OC-Agenten über die OpenResponses-API (`/v1/responses`). |
| **OC → MTHO** | Dateien im gemeinsamen Workspace | OC (oder ein Agent) legt JSON-Einreichungen in `workspace/rat_submissions/` ab; MTHO liest sie per Skript und übernimmt sie in `data/rat_submissions/` (für den OMEGA_ATTRACTOR Council / weitere Verarbeitung). |

---

## Schnittstelle im Backend (angeboten)

Das Backend bietet die OC-Schnittstelle unter **`/api/oc/`** an. So können MTHO und OC (bzw. Cursor/Cloud Agents) austauschen, ohne dass Skripte von Hand gestartet werden müssen.

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/api/oc/status` | GET | Gateway erreichbar? (Konfiguration + Erreichbarkeit) |
| `/api/oc/send` | POST | Nachricht an OC senden (Body: `{"text": "...", "agent_id": "main"}`) |
| `/api/oc/fetch` | GET oder POST | Einreichungen von OC abholen (OC → MTHO), speichert in `data/rat_submissions/` |

Backend starten (z. B. über `START_BACKEND_SERVICES.bat` oder `uvicorn`), dann z. B.:  
`GET http://localhost:8000/api/oc/status` oder `POST http://localhost:8000/api/oc/send` mit JSON-Body.

---

## MTHO → OC: Nachricht an Agent senden

- **API:** OpenClaw Gateway `POST /v1/responses` (OpenResponses-kompatibel).
- **Voraussetzung:** Im Gateway muss `gateway.http.endpoints.responses.enabled: true` gesetzt sein. Das VPS-Setup (`setup_vps_hostinger.py`) setzt das bereits.
- **Code:** `src/network/openclaw_client.py` – `send_message_to_agent(text, agent_id="main", user=None)`.
- **Parameter:**
  - `text`: Nachricht an den Agenten.
  - `agent_id`: z. B. `"main"` (Standard-Agent).
  - `user`: optional, für stabile Session (gleicher User = gleiche Session).
- **Rückgabe:** `(success, response_text)` – bei Erfolg die Antwort des Agenten (oder Fehlermeldung).

**Beispiel (Skript oder REPL):**
```python
from src.network.openclaw_client import send_message_to_agent
ok, msg = send_message_to_agent("Hallo OC, hier ist MTHO. Bitte bestätige Empfang.")
print(ok, msg)
```

**Test:** Siehe `src/scripts/test_atlas_oc_channel.py` (prüft Erreichbarkeit und optional Senden einer Testnachricht). Alle Szenarien (inkl. „Daten bei OC“, Frontend-Backend): [TEST_SZENARIEN_OC_UND_FRONTEND.md](../05_AUDIT_PLANNING/TEST_SZENARIEN_OC_UND_FRONTEND.md).

**Hinweis bei 405 (Method Not Allowed):** Das Endpoint ist standardmäßig deaktiviert. **Ohne Browser:** `python -m src.scripts.enable_oc_responses_vps` – setzt per SSH die Config in `/var/lib/openclaw/openclaw.json` und startet OpenClaw-Container neu. Wenn 405 danach bleibt: Der Container, der auf deinem gemappten Port (z. B. 58105) läuft, liest die Config vermutlich nicht von diesem Pfad (z. B. Hostinger-Panel steuert nur per UI). Dann entweder im Panel nach einer Option für „Responses“/„OpenResponses“/HTTP-POST suchen oder VPS-Setup nutzen: `python -m src.scripts.setup_vps_hostinger` (eigener Container mit dieser Config).

**Timeout – Gateway nicht erreichbar:** Der Test läuft von deinem PC aus gegen `http://VPS_HOST:OPENCLAW_GATEWAY_PORT`. **Port:** Bei Hostinger ist oft der **Container-PORT** (z. B. 58105 im Panel) der von außen erreichbare Port – in .env dann `OPENCLAW_GATEWAY_PORT=58105` setzen, nicht 18789. Typische Ursachen: (1) **Falscher Port** – OPENCLAW_GATEWAY_PORT muss dem gemappten Port im Panel entsprechen (z. B. 58105); (2) **Firewall auf dem VPS** – diesen Port von außen freigeben; (3) **Gateway hört nur auf localhost** – HTTP-Server auf 0.0.0.0 binden; (4) **VPS_HOST** in .env = öffentliche IP/Domain des VPS. Test: `curl -v http://DEIN_VPS:58105/` (bzw. den Port aus dem Panel verwenden).

---

## OC → MTHO: Einreichungen für den Osmium OMEGA_ATTRACTOR Council

OC (oder ein Agent auf OC) kann **Themen, Vorschläge oder Fragen** an MTHO/den OMEGA_ATTRACTOR Council übermitteln, indem JSON-Dateien in einem festen Verzeichnis abgelegt werden. MTHO holt sie per Skript ab.

### Ablageort (auf dem VPS, für OC erreichbar)

- **Verzeichnis:** `/var/lib/openclaw/workspace/rat_submissions/`  
  (wird beim VPS-Setup und beim Anlegen der Stammdokumente mit angelegt; OC hat Lese-/Schreibzugriff im Workspace.)

### Schema einer Einreichung (JSON)

Jede Datei: eine JSON-Datei, z. B. `2025-02-25T14-30-00_oc-1.json`.

```json
{
  "from": "oc",
  "type": "rat_submission",
  "created": "2025-02-25T14:30:00Z",
  "payload": {
    "topic": "Kurztitel des Themas",
    "body": "Ausführlicher Text: Vorschlag, Frage oder Info für den OMEGA_ATTRACTOR Council.",
    "priority": "optional: low|normal|high",
    "context": {}
  }
}
```

- **type:** `rat_submission` (für Abstimmung/Entscheidung), `info` (nur zur Kenntnis), `question` (Frage an MTHO/Marc).
- **payload:** frei erweiterbar; `topic` und `body` sind die Mindestangaben für den OMEGA_ATTRACTOR Council.

### Abholen der Einreichungen (MTHO-Seite)

**Skript:** `src/scripts/fetch_oc_submissions.py`

- Verbindet per SSH mit dem VPS.
- Liest alle `.json` in `workspace/rat_submissions/`.
- Speichert sie lokal unter **`data/rat_submissions/`**.
- Verschiebt die gelesenen Dateien auf dem VPS nach `workspace/rat_submissions_archive/`, damit sie nicht doppelt verarbeitet werden.

**Aufruf:**
```bash
python -m src.scripts.fetch_oc_submissions
python -m src.scripts.fetch_oc_submissions --dry-run   # nur anzeigen
```

**.env:** `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` (wie beim übrigen VPS-Zugriff).

### Einbindung in den OMEGA_ATTRACTOR Council

Die abgeholten Dateien in `data/rat_submissions/` können von Marc oder von einem Review-Prozess (z. B. Cursor/Cloud Agents) gelesen werden, um Punkte von OC in die OMEGA_ATTRACTOR Council-Abstimmung oder in die Umsetzungsplanung aufzunehmen.

---

## Testen des Kanals

1. **MTHO → OC (Gateway erreichbar + Nachricht senden):**  
   `python -m src.scripts.test_atlas_oc_channel`  
   Prüft `check_gateway()` und optional `send_message_to_agent("Test")`.

2. **OC → MTHO:**  
   Manuell eine Test-JSON-Datei in `rat_submissions/` auf dem VPS anlegen (per SSH oder über einen OC-Agenten), dann `fetch_oc_submissions` ausführen und prüfen, ob die Datei in `data/rat_submissions/` landet.

---

## Sicherheit und Grenzen

- **MTHO → OC:** Zugriff nur mit gültigem `OPENCLAW_GATEWAY_TOKEN`; Gateway sollte nicht ohne Absicherung ins Internet gebunden werden (Firewall, ggf. nur aus MTHO-Netz erreichbar).
- **OC → MTHO:** OC schreibt nur in sein Workspace-Verzeichnis; MTHO liest per SSH mit VPS-Credentials. Kein direkter HTTP-Call von OC zu MTHO nötig (4D_RESONATOR (MTHO_CORE) muss nicht von außen erreichbar sein).
- **Letzte Instanz:** Lokales MTHO behält die Entscheidungsgewalt; Einreichungen von OC sind Input für den OMEGA_ATTRACTOR Council, keine automatische Ausführung.

---

## Referenzen

- OpenClaw OpenResponses API: [docs.openclaw.ai/gateway/openresponses-http-api](https://docs.openclaw.ai/gateway/openresponses-http-api)
- `openclaw_client.py`, `fetch_oc_submissions.py`, `setup_vps_hostinger.py` (Gateway-Config, rat_submissions-Verzeichnis)

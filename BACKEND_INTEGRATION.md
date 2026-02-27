\# ATLAS Dev Agent - Backend Integration Guide



Dieses Dokument beschreibt, wie das Frontend des ATLAS Dev Agents an ein reales Backend angebunden werden sollte. 



Da es sich um eine interaktive Chat-Anwendung mit Echtzeit-Statusanzeigen und asynchronen System-Events handelt, empfehlen wir eine \*\*hybride Architektur aus WebSockets (für Echtzeit-Kommunikation) und REST (für gezielte Aktionen)\*\*.



---



\## 1. Architektur-Empfehlung



\*   \*\*WebSockets (z.B. Socket.io oder native WS):\*\* 

&nbsp;   \*   Senden von User-Nachrichten an den Agenten.

&nbsp;   \*   Empfangen von Agenten-Antworten (ggf. als Stream).

&nbsp;   \*   Empfangen von asynchronen System-Nachrichten (z.B. Pipeline-Status, Auth-Fehler).

&nbsp;   \*   Echtzeit-Updates für die Status-Indikatoren (Online/Offline).

\*   \*\*REST API:\*\*

&nbsp;   \*   Auslösen von spezifischen Skripten (z.B. Neustart eines Services).

&nbsp;   \*   Abrufen der initialen Chat-Historie beim Laden der Seite.



---



\## 2. Datenmodelle (JSON)



Das Frontend erwartet Nachrichten und Status-Updates in folgenden Formaten:



\### Message Object

```json

{

&nbsp; "id": "unique-uuid-1234",

&nbsp; "role": "user" | "agent" | "external",

&nbsp; "sender": "You" | "Atlas" | "Service-A (Pipeline)",

&nbsp; "content": "Der eigentliche Text der Nachricht...",

&nbsp; "timestamp": "2026-02-25T11:45:00Z"

}

```

\*Hinweis: Wenn `role` auf `"external"` gesetzt ist, wird die Nachricht im Frontend automatisch farblich (blau/indigo) hervorgehoben.\*



\### Service Status Object

```json

{

&nbsp; "service": "Comm Chain",

&nbsp; "status": "online" | "offline" | "restarting"

}

```



---



\## 3. WebSocket Events (Echtzeit-Kommunikation)



Das Backend sollte einen WebSocket-Server bereitstellen, auf den sich das Frontend verbindet.



\### Client -> Server (Frontend sendet an Backend)

\*   \*\*`chat:send`\*\*

&nbsp;   \*   \*Payload:\* `{ "content": "Baue mir eine neue Komponente..." }`

&nbsp;   \*   \*Aktion:\* Der User schickt eine Nachricht an den ATLAS Agenten.



\### Server -> Client (Backend sendet an Frontend)

\*   \*\*`chat:reply`\*\*

&nbsp;   \*   \*Payload:\* `Message Object` (role: "agent")

&nbsp;   \*   \*Aktion:\* Der ATLAS Agent antwortet dem User.

\*   \*\*`system:event`\*\*

&nbsp;   \*   \*Payload:\* `Message Object` (role: "external")

&nbsp;   \*   \*Aktion:\* Ein externes System (z.B. CI/CD, Database) pusht eine Info in den Dev-Channel.

\*   \*\*`status:update`\*\*

&nbsp;   \*   \*Payload:\* `Service Status Object`

&nbsp;   \*   \*Aktion:\* Aktualisiert die kleinen Ampel-Indikatoren oben rechts (z.B. wenn die "Comm Chain" abbricht).



---



\## 4. REST API Endpunkte (Aktionen)



Für direkte, synchrone Aktionen (wie das Klicken auf den Restart-Button eines offline Services).



\### `POST /api/services/:serviceName/restart`

\*   \*\*Beschreibung:\*\* Wird aufgerufen, wenn der User im Frontend auf das rote "Restart"-Icon neben einem Offline-Service klickt.

\*   \*\*Request:\*\* `POST /api/services/Comm%20Chain/restart`

\*   \*\*Response (200 OK):\*\* `{ "success": true, "message": "Restart script initiated" }`

\*   \*Hinweis:\* Das Frontend setzt den Status dann lokal auf `restarting` (gelb drehend). Sobald das Backend fertig ist, sollte es ein WebSocket-Event `status:update` mit `status: "online"` schicken.



\### `GET /api/chat/history` (Optional)

\*   \*\*Beschreibung:\*\* Lädt die letzten X Nachrichten beim initialen Seitenaufruf.

\*   \*\*Response:\*\* `\[ MessageObject, MessageObject, ... ]`



---



\## 5. Was muss im Frontend-Code (App.tsx) noch angepasst werden?



Sobald das Backend steht, müssen im Frontend (`src/App.tsx`) nur die aktuellen "Mocks" (die `setTimeout` Funktionen) durch echte API-Calls ersetzt werden:



1\.  \*\*WebSocket Client integrieren:\*\* z.B. `const ws = new WebSocket('wss://api.euredomain.com/ws')` in einem `useEffect` Hook initialisieren.

2\.  \*\*`handleSend` anpassen:\*\* Statt `setTimeout` wird `ws.send(JSON.stringify({ type: 'chat:send', content: input }))` aufgerufen.

3\.  \*\*`handleRestartService` anpassen:\*\* Statt eines Timeouts wird ein `fetch('/api/services/' + name + '/restart', { method: 'POST' })` ausgeführt.

4\.  \*\*Event Listener hinzufügen:\*\* Ein `ws.onmessage` Listener, der eingehende Nachrichten (`chat:reply` oder `system:event`) direkt in den `setMessages` State pusht.

---

## 6. Umgesetzte Integration (ATLAS_CORE)

- **Backend:** `src/api/routes/dev_agent_ws.py` – WebSocket `/ws` (chat:send → Dev-Agent → chat:reply), REST `POST /api/services/{service_name}/restart`, `GET /api/chat/history`. CORS in `src/api/main.py` für Frontend-Origin (z. B. localhost:3000).
- **Frontend:** `frontend/src/App.tsx` – WebSocket-Client (VITE_ATLAS_API_URL → wsUrl), handleSend sendet `chat:send`, onmessage verarbeitet `chat:reply`, `system:event`, `status:update`; handleRestartService nutzt `fetch(POST …/restart)`; optionales Laden von `/api/chat/history` beim Start.
- **Starten:** Backend: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000` (aus Projekt-Root). Frontend: `cd frontend && npm run dev` (Port 3000). In `frontend/.env`: `VITE_ATLAS_API_URL=http://localhost:8000`.
- **Ein-Klick-Start (Windows):** `START_DEV_AGENT.bat` im Projekt-Root doppelklicken – startet Backend und Frontend in je einem Fenster, wartet 10 Sekunden, oeffnet den Browser auf http://localhost:3000. Zum Beenden die beiden Konsolenfenster schliessen.



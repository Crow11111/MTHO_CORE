# ATLAS Dev Agent - Backend Integration Guide

Dieses Dokument beschreibt, wie das Frontend des ATLAS Dev Agents an ein reales Backend angebunden werden sollte. 

Da es sich um eine interaktive Chat-Anwendung mit Echtzeit-Statusanzeigen und asynchronen System-Events handelt, empfehlen wir eine **hybride Architektur aus WebSockets (für Echtzeit-Kommunikation) und REST (für gezielte Aktionen)**.

---

## 1. Architektur-Empfehlung

*   **WebSockets (z.B. Socket.io oder native WS):** 
    *   Senden von User-Nachrichten an den Agenten.
    *   Empfangen von Agenten-Antworten (ggf. als Stream).
    *   Empfangen von asynchronen System-Nachrichten (z.B. Pipeline-Status, Auth-Fehler).
    *   Echtzeit-Updates für die Status-Indikatoren (Online/Offline).
*   **REST API:**
    *   Auslösen von spezifischen Skripten (z.B. Neustart eines Services).
    *   Abrufen der initialen Chat-Historie beim Laden der Seite.

---

## 2. Datenmodelle (JSON)

Das Frontend erwartet Nachrichten und Status-Updates in folgenden Formaten:

### Message Object
```json
{
  "id": "unique-uuid-1234",
  "role": "user" | "agent" | "external",
  "sender": "You" | "Atlas" | "Service-A (Pipeline)",
  "content": "Der eigentliche Text der Nachricht...",
  "timestamp": "2026-02-25T11:45:00Z"
}
```
*Hinweis: Wenn `role` auf `"external"` gesetzt ist, wird die Nachricht im Frontend automatisch farblich (blau/indigo) hervorgehoben.*

### Service Status Object
```json
{
  "service": "Comm Chain",
  "status": "online" | "offline" | "restarting"
}
```

---

## 3. WebSocket Events (Echtzeit-Kommunikation)

Das Backend sollte einen WebSocket-Server bereitstellen, auf den sich das Frontend verbindet.

### Client -> Server (Frontend sendet an Backend)
*   **`chat:send`**
    *   *Payload:* `{ "content": "Baue mir eine neue Komponente..." }`
    *   *Aktion:* Der User schickt eine Nachricht an den ATLAS Agenten.

### Server -> Client (Backend sendet an Frontend)
*   **`chat:reply`**
    *   *Payload:* `Message Object` (role: "agent")
    *   *Aktion:* Der ATLAS Agent antwortet dem User.
*   **`system:event`**
    *   *Payload:* `Message Object` (role: "external")
    *   *Aktion:* Ein externes System (z.B. CI/CD, Database) pusht eine Info in den Dev-Channel.
*   **`status:update`**
    *   *Payload:* `Service Status Object`
    *   *Aktion:* Aktualisiert die kleinen Ampel-Indikatoren oben rechts (z.B. wenn die "Comm Chain" abbricht).

---

## 4. REST API Endpunkte (Aktionen)

Für direkte, synchrone Aktionen (wie das Klicken auf den Restart-Button eines offline Services).

### `POST /api/services/:serviceName/restart`
*   **Beschreibung:** Wird aufgerufen, wenn der User im Frontend auf das rote "Restart"-Icon neben einem Offline-Service klickt.
*   **Request:** `POST /api/services/Comm%20Chain/restart`
*   **Response (200 OK):** `{ "success": true, "message": "Restart script initiated" }`
*   *Hinweis:* Das Frontend setzt den Status dann lokal auf `restarting` (gelb drehend). Sobald das Backend fertig ist, sollte es ein WebSocket-Event `status:update` mit `status: "online"` schicken.

### `GET /api/chat/history` (Optional)
*   **Beschreibung:** Lädt die letzten X Nachrichten beim initialen Seitenaufruf.
*   **Response:** `[ MessageObject, MessageObject, ... ]`

---

## 5. Was muss im Frontend-Code (App.tsx) noch angepasst werden?

Sobald das Backend steht, müssen im Frontend (`src/App.tsx`) nur die aktuellen "Mocks" (die `setTimeout` Funktionen) durch echte API-Calls ersetzt werden:

1.  **WebSocket Client integrieren:** z.B. `const ws = new WebSocket('wss://api.euredomain.com/ws')` in einem `useEffect` Hook initialisieren.
2.  **`handleSend` anpassen:** Statt `setTimeout` wird `ws.send(JSON.stringify({ type: 'chat:send', content: input }))` aufgerufen.
3.  **`handleRestartService` anpassen:** Statt eines Timeouts wird ein `fetch('/api/services/' + name + '/restart', { method: 'POST' })` ausgeführt.
4.  **Event Listener hinzufügen:** Ein `ws.onmessage` Listener, der eingehende Nachrichten (`chat:reply` oder `system:event`) direkt in den `setMessages` State pusht.

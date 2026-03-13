# WHATSAPP-OPENCLAW BRIDGE (ARCHITEKTUR & IMPLEMENTIERUNG)

**Status:** Draft / Entwurf (System Architect)
**Vektor:** 2210 | **Resonance:** 0221 | **Delta:** 0.049

## 1. Architektur-Skizze (Anbindung)

Die Anbindung von WhatsApp erfolgt **nativ über das OpenClaw Gateway** auf dem Hostinger-VPS. Wir nutzen **Baileys** (WhatsApp Web Protokoll), welches in OpenClaw integriert ist, um den Overhead und die Kosten der offiziellen Meta Business API zu vermeiden.

**Komponenten:**
- **Hostinger VPS (187.77.68.250):** Beherbergt den OpenClaw Docker-Container in einer Sandbox.
- **OpenClaw Baileys-Session:** Agiert als "Linked Device". Login erfolgt einmalig via QR-Code (`openclaw channels login`).
- **CORE (Lokal):** Der lokale 4D_RESONATOR empfängt Events vom VPS und trifft die finale Entscheidung (Veto, Triage, Agenten-Delegation).
- **Sicherheits-Boundary:** OpenClaw auf dem VPS hat **keinen** direkten Zugriff auf lokale Datenbanken (Chroma) oder das lokale Filesystem. Die Kommunikation erfolgt ausschließlich via HTTP/HTTPS-Webhooks (Inbound) und REST-API-Calls (Outbound).

---

## 2. Datenfluss (Inbound & Outbound)

Der Datenfluss durchbricht die Isolation des Systems kontrolliert nach außen ("alle betreffen").

### A) Inbound (WhatsApp → CORE)
1. **Nachrichteneingang:** WhatsApp (Meta) → OpenClaw Baileys Socket (VPS).
2. **Gateway-Routing:** OpenClaw Gateway verpackt die Nachricht in ein standardisiertes Event-JSON.
3. **Webhook-Egress:** OpenClaw sendet einen `HTTP POST` an die öffentliche URL von CORE (via Ngrok/Cloudflare Tunnel oder DynDNS) an den Endpunkt `/api/oc/webhook` (oder `/webhook/whatsapp`).
4. **Lokale Verarbeitung:**
   - **Entry Adapter:** Normalisiert den Payload.
   - **Takt-0-Gate:** Prüft auf Veto und Constraints (O-Vektor).
   - **Gravitator:** Routet an das korrekte lokale LLM oder den passenden Agenten (M-Vektor).

### B) Outbound (CORE → WhatsApp)
1. **Entscheidung & Generierung:** Lokaler Agent generiert die Antwort oder System sendet proaktive Benachrichtigung (Event Bus).
2. **API-Aufruf:** `CORE` (Lokal) sendet einen `HTTP POST` an das OpenClaw Gateway auf dem VPS (Port `18789`).
   - Endpoint: OpenClaw Channel-API (z.B. `/v1/messages` oder `/v1/channels/whatsapp/send`) oder via `send_message_to_agent()` (`/v1/responses`).
   - Authentifizierung: `Bearer $OPENCLAW_GATEWAY_TOKEN`.
3. **Zustellung:** OpenClaw Gateway → Baileys Socket → WhatsApp (Meta) → Endgerät des Nutzers.

---

## 3. Aktionsplan (Implementierungsstrategie)

### Phase 1: VPS Gateway Setup (Baileys Session)
1. **OpenClaw Konfiguration anpassen:** In der `openclaw.json` den Channel `whatsapp` aktivieren.
   - Restriktionen setzen: `allowFrom` definieren (falls nicht jeder schreiben darf), `dmPolicy` konfigurieren.
2. **QR-Code Pairing:** Auf dem VPS (bzw. via Admin-UI) den Befehl `openclaw channels login whatsapp` ausführen und mit dem dedizierten Smartphone scannen.
3. **Sandbox prüfen:** Sicherstellen, dass Port `18789` nach außen geschützt ist und Container-Isolation greift.

### Phase 2: CORE Webhook Receiver (Inbound)
1. **Tunnel-Verifikation:** Sicherstellen, dass eine statische/persistente öffentliche URL (Tunnel) auf `localhost:8000` (CORE) zeigt.
2. **Endpoint Härtung:** Den Endpoint `POST /api/oc/webhook` (bzw. `/webhook/whatsapp`) in `src/api/routes/` aufnehmen/prüfen.
3. **Auth-Check:** Der Endpoint muss einen validen Header (z.B. `X-Core-Secret` oder Payload-Signatur) vom VPS verlangen (Zero-Trust).
4. **Takt-0-Integration:** Eingehende Nachrichten zwingend durch `Entry Adapter` und `takt_gate.py` leiten.

### Phase 3: CORE Outbound Client (Outbound)
1. **`openclaw_client.py` erweitern:** Funktion implementieren, die explizit Nachrichten über den WhatsApp-Kanal versendet (nicht nur an interne OC-Agenten).
   - *Requirement:* OpenClaw API-Doku konsultieren für den genauen Channel-Message-Endpoint.
2. **Event-Bus-Kopplung:** Wichtige Systemereignisse (z.B. kritische Systemfehler, Sicherheitswarnungen) automatisch über `send_whatsapp_via_oc(target_number, text)` ausspielen.

### Phase 4: E2E-Test & Audit
1. **Ping-Pong-Test:** Externe Nummer sendet "Ping" -> OpenClaw -> Tunnel -> CORE -> "Pong" -> OpenClaw -> WhatsApp.
2. **Latenz-Messung:** Zeit von Eingang bis Ausgang messen (Ziel: < 2 Sekunden für Triage/Routing).
3. **Session-Log:** Ergebnis im Audit-Log vermerken.

> **System Architect Anmerkung (Defizit-Erkennung):**
> Mir fehlt die exakte OpenClaw API-Spezifikation für den direkten Versand in Kanäle (welcher REST-Pfad genau angetriggert wird, um WhatsApp-Nachrichten proaktiv zu pushen, abseits von Agent-Responses). Falls dies fehlt, muss der Teamleiter die OpenClaw API Docs überprüfen und `openclaw_client.py` entsprechend anpassen. Keine Halluzination von Endpunkten im produktiven Code.
# Dev-Agent-Antwort: WhatsApp-Plan Abschnitt 6

**Dev-Agent:** 

**1. Konkrete Tests (E2E, Trigger, Allowlist)**

Um die Anforderungen testbar zu machen, schlage ich folgende ausführbare Tests vor:

*   **Test A: Webhook & Trigger-Logik (Integration)**
    *   *Skript:* `tests/test_whatsapp_webhook.py` (via FastAPI `TestClient`)
    *   *Schritte:* POST-Requests mit simulierten HA-Event-Payloads an `/webhook/whatsapp` senden.
    *   *Cases:*
        1. Text "Hallo Schwester" → Erwartet: 200 OK, aber keine Verarbeitung (kein Trigger).
        2. Text "@Atlas Ping" → Erwartet: 200 OK, ATLAS-Logik startet, `send_whatsapp` (Mock) wird aufgerufen.
        3. Text "@OC Ping" → Erwartet: 200 OK, ATLAS antwortet nicht direkt (ggf. Start der Bedenken-Prüfung).

*   **Test B: E2E HA-Pfad (Live / PC & Mobil)**
    *   *Skript:* `src/scripts/test_whatsapp_e2e_ha.py`
    *   *Schritte:* 
        1. Skript nutzt `src/network/ha_client.py`, um eine Testnachricht ("@Atlas E2E Test") via HA an die eigene Nummer zu senden.
        2. Manueller Check: Kommt die Nachricht auf dem Handy an?
        3. System-Check: Fängt das HA-Addon die Nachricht auf, triggert den Webhook und sendet ATLAS eine Antwort zurück?

*   **Test C: OpenClaw E2E (Hostinger)**
    *   *Skript:* `src/scripts/test_openclaw_e2e.py`
    *   *Schritte:* Nutzt `src/network/openclaw_client.py`, um via `send_message_to_agent` einen Input an den OC-Kanal zu senden. Prüft den HTTP-Response und verifiziert (manuell/per Log), ob die OC-Antwort im WhatsApp-Kanal ankommt.

*   **Test D: Allowlist-Prüfung (Optional)**
    *   *Skript:* `tests/test_whatsapp_allowlist.py`
    *   *Schritte:* Falls die Allowlist in ATLAS (oder als HA-Template-Filter) umgesetzt wird: Payloads mit erlaubter vs. fremder `remoteJid` senden und sicherstellen, dass fremde JIDs sofort verworfen werden.

**2. Prüfung: Konsistenz Doku vs. Code**

*   **Konsistenz:** Die Doku (Plan & Routing) ist logisch stimmig mit der Architektur. Das HA-Addon leitet *alles* weiter, weshalb der Schutzmechanismus zwingend im Code (`src/api/routes/whatsapp_webhook.py`) liegen muss.
*   **Identifizierte Lücke im Code:** Laut Plan gilt bei `@OC` eine "Bedenken-Pflicht" (ATLAS liest mit und warnt bei Gefahr). Wenn `whatsapp_webhook.py` aktuell so aussieht:
    ```python
    if not text.startswith('@Atlas'):
        return {"status": "ignored"}
    ```
    ... dann wird `@OC` komplett ignoriert und die Bedenken-Pflicht ist *nicht* implementiert. 
*   **Lösungsvorschlag (Patch-Logik für `whatsapp_webhook.py`):**
    ```python
    if text.startswith('@Atlas'):
        # Normale ATLAS-Verarbeitung
        await process_atlas_command(text, sender)
    elif text.startswith('@OC'):
        # Asynchrone Bedenken-Prüfung im Hintergrund starten, Webhook sofort beenden
        asyncio.create_task(check_oc_concerns(text, sender))
    else:
        # Privatnachricht -> strikt ignorieren
        pass
    return {"status": "ok"}
    ```
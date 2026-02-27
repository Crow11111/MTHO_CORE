===== ANTWORT VOM DEV-AGENT (Gemini) =====

Hier ist die Checkliste für `docs/DEV_AGENT_OC_KANAL_CHECKLISTE.md`.

***

# DEV_AGENT_OC_KANAL_CHECKLISTE

## Empfohlene Reihenfolge (Kanal vs. Stammdokumente)
1. **Zuerst Stammdokumente deployen:** `python src/scripts/deploy_stammdokumente_vps.py`
2. **Dann Kanal fixen & testen** (siehe Checkliste unten).
3. **Zuletzt OC informieren:** Kurze WhatsApp-Info ("Stammdokumente liegen auf VPS im Workspace, erste Test-Payload via `/v1/responses` ist raus").

---

## Checkliste: ATLAS-OC-Kanal Setup

### 1) VPS-Config prüfen/ergänzen
*   **Was tun:** OpenClaw-Konfiguration auf dem VPS prüfen (meist `openclaw.json` oder via Environment-Variablen).
*   **Was prüfen:** Sicherstellen, dass der Responses-Endpoint aktiviert ist.
    ```json
    "gateway": {
      "http": {
        "endpoints": {
          "responses": { "enabled": true }
        }
      }
    }
    ```
    *(Alternativ: Prüfen, ob `src/scripts/setup_vps_hostinger.py` dies korrekt gesetzt hat).*
*   **Typische Fehler:** "Nicht konfiguriert" – OC lehnt Anfragen ab, wenn der Endpoint auf `false` steht oder fehlt.

### 2) Container-Neustart (einmal ausführen)
*   **Was tun:** OpenClaw-Container auf dem VPS neustarten – damit die Config greift.
*   **So geht’s (ein Befehl):**
    ```bash
    python -m src.scripts.restart_openclaw_vps
    ```
    Das Skript verbindet per SSH (VPS_HOST, VPS_USER, VPS_PASSWORD aus .env) und führt `docker restart openclaw-gateway` aus.
*   **Was prüfen:** Danach ca. 10 s warten, dann `python -m src.scripts.test_atlas_oc_channel --send` – sollte OK melden.
*   **Typische Fehler:** Ohne Neustart werden Änderungen aus Schritt 1 ignoriert (weiterhin 405).

### 3) `test_atlas_oc_channel --send`
*   **Was tun:** Lokalen Test-Call an das Gateway absetzen.
    ```bash
    python src/scripts/test_atlas_oc_channel.py --send
    ```
*   **Was prüfen:** Skript muss einen Erfolgs-Status (HTTP 200 oder 202) zurückgeben.
*   **Typische Fehler:**
    *   **405 Method Not Allowed:** Endpoint ist in der OC-Config nicht aktiviert oder Container wurde nicht neu gestartet (siehe 1 & 2).
    *   **Timeout:** Falsche `gateway_url` in `src/network/openclaw_client.py`, Container down oder VPS-Firewall blockiert den Port.
    *   **401/403 Unauthorized:** `auth_headers` (API-Key) in `openclaw_client.py` fehlen oder sind falsch.

### 4) `send_offene_punkte_to_oc`
*   **Was tun:** Echte Nutzdaten (Kontext + offene Punkte) an OC senden.
    ```bash
    python src/scripts/send_offene_punkte_to_oc.py
    ```
*   **Was prüfen:** Skript läuft ohne Exception durch. OC-Team bestätigen lassen, dass die Payload im System angekommen ist.
*   **Typische Fehler:**
    *   Gleiche Netzwerk-Fehler wie in Schritt 3.
    *   **400 Bad Request:** Payload-Format weicht von dem ab, was OC erwartet (JSON-Struktur in `send_message_to_agent` prüfen).

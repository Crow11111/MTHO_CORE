# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import requests
import os
import sys
import urllib3

# Suppress InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Konfiguration
HASS_IP = "192.168.178.54"
HASS_PORT = "8123"
HASS_URL = f"https://{HASS_IP}:{HASS_PORT}"

# Token aus Environment oder Hardcoded (Fallback/Test)
# Hier erwarten wir, dass es via Environment kommt oder wir lesen es manuell für diesen Run
# Da ich das Skript schreibe, hole ich das Token aus dem Environment, das im Shell-Kontext gesetzt sein sollte.
# Falls nicht, lese ich .env Datei manuell (quick & dirty für standalone script).

def get_token():
    token = os.getenv("HASS_TOKEN")
    if token:
        return token
    
    # Fallback: Versuche .env Datei zu lesen
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("HASS_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return None

TOKEN = get_token()

if not TOKEN:
    print("FEHLER: Kein HASS_TOKEN gefunden.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def main():
    print(f"Starte Säuberung auf {HASS_URL}...")
    
    # 1. Hole alle States
    try:
        response = requests.get(f"{HASS_URL}/api/states", headers=HEADERS, verify=False)
        response.raise_for_status()
        states = response.json()
    except Exception as e:
        print(f"FEHLER beim Abrufen der States: {e}")
        sys.exit(1)

    phantoms = []
    for state in states:
        if state["state"] == "unavailable" and state.get("attributes", {}).get("restored") is True:
            phantoms.append(state["entity_id"])

    print(f"Gefundene Phantome (unavailable + restored): {len(phantoms)}")

    deleted_count = 0
    failed_count = 0

    # 2. Lösche Phantome
    for entity_id in phantoms:
        # Versuch 1: /api/config/entity_registry/entry/{entity_id}
        url = f"{HASS_URL}/api/config/entity_registry/entry/{entity_id}"
        try:
            # print(f"Lösche {entity_id}...")
            del_response = requests.delete(url, headers=HEADERS, verify=False)
            
            if del_response.status_code in [200, 204]:
                print(f"[OK] Gelöscht: {entity_id}")
                deleted_count += 1
            elif del_response.status_code == 404:
                 # Versuch 2: /api/config/entity_registry/{entity_id} (alter Pfad)
                url_old = f"{HASS_URL}/api/config/entity_registry/{entity_id}"
                del_response_old = requests.delete(url_old, headers=HEADERS, verify=False)
                if del_response_old.status_code in [200, 204]:
                    print(f"[OK] Gelöscht (alter Pfad): {entity_id}")
                    deleted_count += 1
                else:
                    if failed_count == 0:
                        print(f"[DEBUG ERSTER FEHLER] {entity_id} - Status: {del_response.status_code} - {del_response.text}")
                    failed_count += 1
            else:
                # API wirft oft Fehler bei Integration-Entities, wir ignorieren es wie befohlen
                # Aber loggen den Status Code für Debug beim ersten Fehler
                if failed_count == 0:
                    print(f"[DEBUG ERSTER FEHLER] {entity_id} - Status: {del_response.status_code} - {del_response.text}")
                failed_count += 1
        except Exception as e:
            print(f"[FEHLER] {entity_id}: {e}")
            failed_count += 1

    print("-" * 30)
    print(f"Exekution beendet.")
    print(f"Entfernt: {deleted_count}")
    print(f"Ignoriert/Fehler: {failed_count} (meist Integration-managed)")

if __name__ == "__main__":
    main()

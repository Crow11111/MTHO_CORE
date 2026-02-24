import asyncio
import os
import json
import sys
from loguru import logger
from dotenv import load_dotenv
import httpx

load_dotenv()

HASS_URL = os.getenv("HASS_URL", "http://192.168.178.54:8123")
HASS_TOKEN = os.getenv("HASS_TOKEN")
OLLAMA_ADDON_SLUG = "76e18fb5_ollama"

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

async def get_addon_state(client: httpx.AsyncClient) -> str:
    """Get the add-on state from the update entity."""
    url = f"{HASS_URL}/api/states/update.ollama_update"
    r = await client.get(url, headers=HEADERS)
    if r.status_code == 200:
        data = r.json()
        logger.info(f"Ollama entity state: {data.get('state')}")
        attrs = data.get("attributes", {})
        logger.info(f"Installed: {attrs.get('installed_version')} | Latest: {attrs.get('latest_version')}")
        return data.get("state", "unknown")
    logger.error(f"Cannot get entity state: {r.status_code}")
    return "unknown"

async def check_ollama_port(client: httpx.AsyncClient) -> bool:
    """Check if Ollama API port 11434 is accessible."""
    try:
        r = await client.get("http://192.168.178.54:11434/api/tags", timeout=5.0)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            logger.success(f"Ollama API reachable! Verfügbare Modelle: {models}")
            return True
        return False
    except Exception as e:
        logger.warning(f"Port 11434 nicht erreichbar: {e}")
        return False

async def start_addon_via_service(client: httpx.AsyncClient) -> bool:
    """Start the Ollama add-on via HA hassio service call."""
    url = f"{HASS_URL}/api/services/hassio/addon_start"
    payload = {"addon": OLLAMA_ADDON_SLUG}
    logger.info(f"Sending addon_start service call for: {OLLAMA_ADDON_SLUG}")
    try:
        r = await client.post(url, headers=HEADERS, json=payload, timeout=30.0)
        logger.info(f"Service call result: {r.status_code} -> {r.text[:200]}")
        return r.status_code in (200, 201)
    except Exception as e:
        logger.error(f"Service call failed: {e}")
        return False

async def main():
    async with httpx.AsyncClient(timeout=15.0) as client:
        logger.info("=== ATLAS: Ollama Raspi5 Aktivierung ===")
        
        # Step 1: Check if port is already open
        if await check_ollama_port(client):
            logger.success("Ollama läuft bereits — port offen. Kein Start nötig.")
            return
        
        # Step 2: check entity state
        await get_addon_state(client)
        
        # Step 3: Try to start via HA service
        logger.info("Starte Add-on über HA service call...")
        started = await start_addon_via_service(client)
        
        if started:
            logger.info("Start-Befehl gesendet. Warte 15s...")
            await asyncio.sleep(15)
            if await check_ollama_port(client):
                logger.success("Ollama ist nun erreichbar! Compilation kann starten.")
            else:
                logger.warning("Port immer noch zu. Ollama braucht evtl. länger zum starten.")
                logger.info("Tipp: Check in HA > Einstellungen > Add-ons > Ollama > Protokoll")
        else:
            logger.error("Service call fehlgeschlagen.")
            logger.info("""
MANUELLER SCHRITT ERFORDERLICH:
1. Öffne http://192.168.178.54:8123
2. Einstellungen > Add-ons > Ollama
3. Klicke 'Starten'
4. Gehe zum Reiter 'Netzwerk'  
5. Stell sicher, dass Port 11434 aktiviert ist
6. Starte das Add-on neu
""")

if __name__ == "__main__":
    asyncio.run(main())

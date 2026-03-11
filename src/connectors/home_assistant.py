# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import httpx
from httpx import AsyncClient, Timeout
from src.utils.time_metric import get_friction_timeout
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


def _should_skip_ssl(url: str) -> bool:
    """SSL-Verifizierung für lokale/private IPs deaktivieren."""
    return "://192.168." in url or "://10." in url or "://172." in url


class HomeAssistantClient:
    def __init__(self):
        self.base_url = os.getenv("HASS_URL") or os.getenv("HA_URL")
        self.token = os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN")
        
        if not self.base_url:
            raise ValueError("HASS_URL environment variable is not set")
        if not self.token:
            raise ValueError("HASS_TOKEN environment variable is not set")

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def get_states(self):
        """Fetch all entity states from Home Assistant."""
        return await self._get_request("states")

    async def get_config(self):
        """Fetch Home Assistant configuration."""
        return await self._get_request("config")

    async def get_services(self):
        """Fetch available services."""
        return await self._get_request("services")

    async def get_automation_config(self):
        """Fetch detailed automation configuration."""
        # Try fetching from registry or different endpoint if direct config fails
        # standard endpoint for editing is /api/config/automation/config/
        return await self._get_request("config/automation/config/")
    
    async def get_script_config(self):
        """Fetch detailed script configuration."""
        return await self._get_request("config/script/config/")

    async def call_service(self, domain, service, service_data=None):
        """Call a Home Assistant service."""
        try:
            verify_ssl = not _should_skip_ssl(self.base_url)
            timeout = get_friction_timeout(10.0)
            async with AsyncClient(timeout=Timeout(timeout), verify=verify_ssl) as client:
                url = f"{self.base_url}/api/services/{domain}/{service}"
                response = await client.post(url, headers=self.headers, json=service_data or {})
                response.raise_for_status()
                logger.info(f"Service call {domain}.{service} successful.")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling service {domain}.{service}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling service {domain}.{service}: {e}")
            return None

    async def speak(self, media_player_entity_id: str, message: str, cache: bool = True):
        """Send a text-to-speech message to a media player."""
        service_data = {
            "entity_id": media_player_entity_id,
            "message": message,
            "cache": cache,
            "language": "de", # Zwingend auf Deutsch stellen, um englischen Akzent zu verhindern
        }
        # Versucht, einen gängigen TTS-Dienst zu nutzen. HA hat viele verschiedene,
        # wir versuchen hier die gängigsten (z.B. google_translate_say, aber auch die neuen Nabu Casa Services)
        # Wenn einer fehlschlägt, versuchen wir den nächsten.
        tts_services_to_try = [
            "tts.google_translate_say",
            "tts.cloud_say", # Nabu Casa
            "tts.google_say" # Ältere Integration
        ]
        
        last_error = None
        verify_ssl = not _should_skip_ssl(self.base_url)
        for service_call in tts_services_to_try:
            domain, service = service_call.split('.')
            try:
                # Wir rufen hier _call_service direkt auf, um mehr Kontrolle zu haben
                timeout = get_friction_timeout(20.0)
                async with AsyncClient(timeout=Timeout(timeout), verify=verify_ssl) as client:
                    url = f"{self.base_url}/api/services/{domain}/{service}"
                    response = await client.post(url, headers=self.headers, json=service_data)
                    if 200 <= response.status_code < 300:
                        logger.info(f"TTS Service call {domain}.{service} successful for message: '{message}'")
                        return {"success": True, "service_used": service_call}
                    else:
                        last_error = f"Service {service_call} returned status {response.status_code}: {response.text}"
                        logger.warning(last_error)
                
            except httpx.HTTPError as e:
                last_error = f"HTTP error calling TTS service {service_call}: {e}"
                logger.warning(last_error)
            except Exception as e:
                last_error = f"Error calling TTS service {service_call}: {e}"
                logger.warning(last_error)
        
        logger.error(f"All TTS service calls failed. Last error: {last_error}")
        return {"success": False, "error": last_error}

    async def _get_request(self, endpoint):
        """Helper for GET requests."""
        try:
            verify_ssl = not _should_skip_ssl(self.base_url)
            timeout = get_friction_timeout(10.0)
            async with AsyncClient(timeout=Timeout(timeout), verify=verify_ssl) as client:
                response = await client.get(f"{self.base_url}/api/{endpoint}", headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching {endpoint}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None

    async def check_connection(self) -> bool:
        """
        Check connection to Home Assistant API.
        Returns True if connection is successful, False otherwise.
        """
        try:
            config = await self.get_config()
            if config:
                logger.info("Connected to Home Assistant: API running.")
                return True
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

if __name__ == "__main__":
    # Quick ad-hoc test
    import asyncio
    
    async def main():
        client = HomeAssistantClient()
        success = await client.check_connection()
        print(f"Connection successful: {success}")

    asyncio.run(main())

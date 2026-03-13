# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import httpx
from src.utils.time_metric import get_friction_timeout
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def _should_skip_ssl(url: str) -> bool:
    """SSL-Verifizierung fuer lokale/private IPs deaktivieren."""
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
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            verify_ssl = not _should_skip_ssl(self.base_url)
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=httpx.Timeout(20.0),
                verify=verify_ssl,
            )
        return self._client

    async def close(self):
        """Persistenten HTTP-Client schliessen."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

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
            client = await self._get_client()
            timeout = get_friction_timeout(10.0)
            response = await client.post(
                f"/api/services/{domain}/{service}",
                json=service_data or {},
                timeout=httpx.Timeout(timeout),
            )
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
            "language": "de",
        }
        tts_services_to_try = [
            "tts.google_translate_say",
            "tts.cloud_say",
            "tts.google_say",
        ]

        last_error = None
        client = await self._get_client()
        fallback_timeout = httpx.Timeout(get_friction_timeout(5.0))
        for service_call in tts_services_to_try:
            domain, service = service_call.split('.')
            try:
                response = await client.post(
                    f"/api/services/{domain}/{service}",
                    json=service_data,
                    timeout=fallback_timeout,
                )
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
            client = await self._get_client()
            timeout = get_friction_timeout(10.0)
            response = await client.get(
                f"/api/{endpoint}", timeout=httpx.Timeout(timeout)
            )
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
    import asyncio

    async def main():
        client = HomeAssistantClient()
        try:
            success = await client.check_connection()
            print(f"Connection successful: {success}")
        finally:
            await client.close()

    asyncio.run(main())

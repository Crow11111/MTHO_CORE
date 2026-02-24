import os
import httpx
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

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
            async with httpx.AsyncClient(timeout=10.0) as client:
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

    async def _get_request(self, endpoint):
        """Helper for GET requests."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
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

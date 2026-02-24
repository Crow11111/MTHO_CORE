import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from connectors.home_assistant import HomeAssistantClient
from dotenv import load_dotenv

async def test_connection():
    load_dotenv()
    print("Testing Home Assistant Connection...")
    print(f"URL: {os.getenv('HASS_URL') or os.getenv('HA_URL')}")
    
    try:
        client = HomeAssistantClient()
        success = await client.check_connection()
        
        if success:
            print("SUCCEEDED: Connected to Home Assistant")
            sys.exit(0)
        else:
            print("FAILED: Could not connect to Home Assistant")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_connection())

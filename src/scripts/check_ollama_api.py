import asyncio
import httpx
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST_1 = "http://192.168.178.54:11434"
OLLAMA_HOST_2 = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

async def check_api(host):
    try:
        url = f"{host}/api/tags"
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(url)
            if r.status_code == 200:
                logger.info(f"Ollama API reachable at {host}")
                models = r.json().get("models", [])
                logger.info(f"Available models: {[m.get('name') for m in models]}")
                return True, host
            else:
                logger.warning(f"Ollama API returned {r.status_code} at {host}")
                return False, host
    except Exception as e:
        logger.warning(f"Cannot reach {host}: {e}")
        return False, host

async def pull_model(host, model):
    logger.info(f"Pulling model '{model}' at {host}...")
    try:
        url = f"{host}/api/pull"
        data = {"name": model}
        async with httpx.AsyncClient(timeout=600.0) as client:
            # this might take a long time, but let's try reading the stream or just fire and forget if it blocks
            r = await client.post(url, json=data)
            if r.status_code == 200:
                logger.info("Model pull initiated/completed successfully.")
            else:
                logger.error(f"Failed to pull model: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Exception pulling model: {e}")

async def main():
    logger.info("Checking API access...")
    
    # Try the HA machine IP first, then localhost fallback
    success, active_host = await check_api(OLLAMA_HOST_1)
    if not success:
        success, active_host = await check_api(OLLAMA_HOST_2)
        
    if success:
        logger.info(f"Using Ollama host: {active_host}")
        await pull_model(active_host, MODEL)
    else:
        logger.error("Could not reach Ollama API. The add-on might still be starting up, or ports are not exposed.")

if __name__ == "__main__":
    asyncio.run(main())

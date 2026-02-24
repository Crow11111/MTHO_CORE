import asyncio
import httpx
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

OLLAMA_HOST = "http://192.168.178.54:11434"
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLD_MODEL = "llama3.1"

async def delete_model(host, model):
    logger.info(f"Attempting to delete model '{model}' at {host}...")
    try:
        url = f"{host}/api/delete"
        data = {"name": model}
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.request("DELETE", url, json=data)
            if r.status_code == 200:
                logger.info(f"Deleted model {model} successfully.")
            elif r.status_code == 404:
                logger.info(f"Model {model} was not found (already deleted or never finished pulling).")
            else:
                logger.error(f"Failed to delete model: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Exception deleting model: {e}")

async def pull_model(host, model):
    logger.info(f"Pulling smaller model '{model}' at {host}...")
    try:
        url = f"{host}/api/pull"
        data = {"name": model}
        async with httpx.AsyncClient(timeout=600.0) as client:
            r = await client.post(url, json=data)
            if r.status_code == 200:
                logger.info("Smaller model pull initiated/completed successfully.")
            else:
                logger.error(f"Failed to pull model: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Exception pulling model: {e}")

async def main():
    logger.info("Managing Ollama models on Raspberry Pi...")
    # Delete the large model
    await delete_model(OLLAMA_HOST, OLD_MODEL)
    # Pull the new small model
    await pull_model(OLLAMA_HOST, MODEL)

if __name__ == "__main__":
    asyncio.run(main())

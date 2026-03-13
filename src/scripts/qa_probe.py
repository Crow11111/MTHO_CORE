# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import sys
import os
import asyncio
import json
import httpx
from loguru import logger
from dotenv import load_dotenv

sys.path.append(os.getcwd())
load_dotenv()

PIPELINE_ID = '01hzktez4kncsm0sr1qx32hy5x'

class HAClient:
    def __init__(self):
        self.base_url = os.getenv('HASS_URL') or os.getenv('HA_URL')
        self.token = os.getenv('HASS_TOKEN') or os.getenv('HA_TOKEN')
        if not self.base_url or not self.token: raise ValueError('Credentials missing')
        if self.base_url.endswith('/'): self.base_url = self.base_url[:-1]
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

    async def probe(self):
        paths = [
            'api/',
            'api/config',
            'api/assist_pipeline/pipeline',
            f'api/assist_pipeline/pipeline/{PIPELINE_ID}',
        ]
        async with httpx.AsyncClient(verify=False) as client:
            for p in paths:
                url = f'{self.base_url}/{p}'
                try:
                    resp = await client.get(url, headers=self.headers)
                    logger.info(f'PROBE {p}: {resp.status_code}')
                    if resp.status_code == 200:
                        logger.info(f'  -> Content: {resp.text[:200]}...')
                except Exception as e:
                    logger.info(f'PROBE {p}: FAIL {e}')

async def main():
    client = HAClient()
    await client.probe()

if __name__ == '__main__':
    asyncio.run(main())

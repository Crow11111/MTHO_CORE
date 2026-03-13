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
TARGET_WAKE_WORD_ID = 'computer_v2'
TARGET_ENTITY = 'wake_word.openwakeword'

class HAClient:
    def __init__(self):
        self.base_url = os.getenv('HASS_URL') or os.getenv('HA_URL')
        self.token = os.getenv('HASS_TOKEN') or os.getenv('HA_TOKEN')
        if not self.base_url or not self.token: raise ValueError('Credentials missing')
        if self.base_url.endswith('/'): self.base_url = self.base_url[:-1]
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}

    async def get_pipeline(self, pid):
        url = f'{self.base_url}/api/assist_pipeline/pipeline/{pid}'
        async with httpx.AsyncClient(verify=False) as client:
            try:
                resp = await client.get(url, headers=self.headers)
                if resp.status_code == 404: 
                    # Try listing if direct access fails
                    url_list = f'{self.base_url}/api/assist_pipeline/pipeline'
                    resp_list = await client.get(url_list, headers=self.headers)
                    if resp_list.status_code == 200:
                        data = resp_list.json()
                        pipelines = data.get('pipelines', []) if isinstance(data, dict) else data
                        for p in pipelines:
                            if p.get('id') == pid: return p
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                # If everything fails, try one more time without pipeline specific endpoint
                raise ValueError(f'Error fetching pipeline: {e}')

    async def update_pipeline(self, pid, data):
        url = f'{self.base_url}/api/assist_pipeline/pipeline/{pid}'
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(url, headers=self.headers, json=data)
            if resp.status_code != 200:
                resp = await client.put(url, headers=self.headers, json=data)
            resp.raise_for_status()
            return resp.json()

async def main():
    try:
        client = HAClient()
        logger.info(f'Connecting to {client.base_url}')
        
        config = await client.get_pipeline(PIPELINE_ID)
        name = config.get('name')
        logger.info(f'Pipeline loaded: {name}')

        ww_id = config.get('wake_word_id')
        ww_ent = config.get('wake_word_entity')
        eng = config.get('conversation_engine')
        
        logger.info(f'Current: WW_ID={ww_id}, Entity={ww_ent}, Engine={eng}')
        
        fix = False
        if ww_ent != TARGET_ENTITY:
            logger.error(f'FAIL Entity: {ww_ent} != {TARGET_ENTITY}')
            config['wake_word_entity'] = TARGET_ENTITY
            fix = True
        else: logger.success('PASS Entity')

        if ww_id != TARGET_WAKE_WORD_ID:
            logger.error(f'FAIL ID: {ww_id} != {TARGET_WAKE_WORD_ID}')
            config['wake_word_id'] = TARGET_WAKE_WORD_ID
            fix = True
        else: logger.success('PASS ID')

        if not eng: logger.error('FAIL Engine Missing')
        else: logger.success(f'PASS Engine: {eng}')

        if fix:
            logger.warning('Fixing...')
            await client.update_pipeline(PIPELINE_ID, config)
            logger.success('FIX APPLIED')
            
            # Re-Verify
            new_config = await client.get_pipeline(PIPELINE_ID)
            new_ww_id = new_config.get('wake_word_id')
            logger.info(f'New WW_ID verified: {new_ww_id}')
        else:
            logger.info('System GREEN')

    except Exception as e:
        logger.exception(f'QA FAILED: {e}')

if __name__ == '__main__':
    asyncio.run(main())

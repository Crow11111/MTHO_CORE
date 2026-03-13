# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import asyncio
import logging
import aiohttp
from typing import Any, Dict, Optional
from .sensor_bus import SensorBus

logger = logging.getLogger(__name__)

class FailoverManager:
    def __init__(self, vps_ping_url: str, dreadnought_ping_url: str, sensor_bus: SensorBus):
        self.vps_ping_url = vps_ping_url
        self.dreadnought_ping_url = dreadnought_ping_url
        self.sensor_bus = sensor_bus
        self.vps_online: bool = False
        self.dreadnought_online: bool = False
        self.heavy_processing_active: bool = False
        self._monitor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._monitor_task = asyncio.create_task(self._monitoring_loop())

    async def stop(self) -> None:
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

    async def _check_endpoint(self, url: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=2.0) as response:
                    return response.status == 200
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return False

    async def _monitoring_loop(self) -> None:
        while True:
            self.vps_online = await self._check_endpoint(self.vps_ping_url)
            self.dreadnought_online = await self._check_endpoint(self.dreadnought_ping_url)

            self.heavy_processing_active = self.dreadnought_online
            if self.dreadnought_online:
                logger.debug("Dreadnought is ON. Heavy processing enabled.")
            else:
                logger.debug("Dreadnought is OFF. Heavy processing disabled.")

            self.sensor_bus.is_vps_reachable = self.vps_online
            if not self.vps_online:
                logger.warning("FailoverManager: VPS is DOWN. Buffering in SensorBus.")
            
            await asyncio.sleep(7.0)  # Primzahl-Zyklus (V6 Zikaden-Prinzip)

    async def route_event(self, sensor_id: str, payload: Dict[str, Any]) -> None:
        if self.heavy_processing_active:
            payload["_heavy_processing"] = True
            
        await self.sensor_bus.publish_event(sensor_id, payload)

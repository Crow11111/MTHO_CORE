# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import asyncio
import logging
import aiohttp
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class SensorBus:
    def __init__(self, vps_endpoint: str, max_queue_size: int = 10000):
        self.vps_endpoint = vps_endpoint
        self.queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=max_queue_size)
        self.flush_task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self.is_vps_reachable: bool = True

    async def start(self) -> None:
        self._session = aiohttp.ClientSession()
        self.flush_task = asyncio.create_task(self._flush_queue_to_brain())

    async def stop(self) -> None:
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                pass
        if self._session:
            await self._session.close()

    async def publish_event(self, sensor_id: str, payload: Dict[str, Any]) -> None:
        event = {"sensor_id": sensor_id, "payload": payload}
        try:
            self.queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.error(f"Sensor queue full. Dropping event from {sensor_id}.")

    async def _flush_queue_to_brain(self) -> None:
        if not self._session:
            raise RuntimeError("Session not initialized.")
        
        while True:
            event = await self.queue.get()
            
            _backoff_attempt = 0
            while not self.is_vps_reachable:
                from src.config.engine_patterns import fibonacci_backoff
                await asyncio.sleep(fibonacci_backoff(_backoff_attempt))
                _backoff_attempt += 1

            try:
                async with self._session.post(self.vps_endpoint, json=event, timeout=5.0) as response:
                    response.raise_for_status()
            except (aiohttp.ClientError, asyncio.TimeoutError):
                logger.warning("VPS unreachable during flush. Requeueing event.")
                self.is_vps_reachable = False
                try:
                    self.queue.put_nowait(event)
                except asyncio.QueueFull:
                    logger.error("Queue full during requeue. Event dropped.")
            finally:
                self.queue.task_done()

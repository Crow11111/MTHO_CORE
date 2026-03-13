# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Ephemeral Agent: Kurzlebige Sub-Instanz fuer Intent-Verarbeitung (Signal-Vektor 2).

Lebenszyklus:
1. Spawn: Bei Intent-Erkennung (Takt 2)
2. Execute: Verarbeitet den spezifischen Intent
3. Report: Liefert Ergebnis an Pool
4. Die: Selbstterminierung nach Erfuellung

Architektur:
- EphemeralAgent: Einzelne Instanz mit TTL
- EphemeralAgentPool: Verwaltet aktive Agents, Garbage Collection

Integration:
- Hoeren: scout_direct_handler.process_text() spawnt Agent bei deep_reasoning
- Sehen: vision_daemon spawnt Agent bei Symmetriebruch-Events
- Sprechen: Agent kann TTS triggern
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine
from loguru import logger


class IntentType(Enum):
    """Intent-Typen fuer Ephemeral Agents (Signal-Vektor 2)."""
    COMMAND = "command"
    DEEP_REASONING = "deep_reasoning"
    VISION_ANALYSIS = "vision_analysis"
    TTS_DISPATCH = "tts_dispatch"
    FAILOVER = "failover"


@dataclass
class EphemeralResult:
    """Ergebnis eines Ephemeral Agent Tasks."""
    success: bool
    intent: IntentType
    payload: Any = None
    error: str | None = None
    duration_ms: float = 0.0


@dataclass
class EphemeralAgent:
    """
    Kurzlebige Sub-Instanz fuer Intent-Verarbeitung.
    Stirbt nach TTL oder nach Erfuellung.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    intent: IntentType = IntentType.COMMAND
    payload: dict = field(default_factory=dict)
    ttl_seconds: float = 30.0
    created_at: float = field(default_factory=time.time)
    completed: bool = False
    result: EphemeralResult | None = None

    @property
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl_seconds

    @property
    def age_ms(self) -> float:
        return (time.time() - self.created_at) * 1000

    async def execute(self, handler: Callable[..., Coroutine[Any, Any, Any]]) -> EphemeralResult:
        """
        Fuehrt den Intent-Handler aus und terminiert.
        """
        start = time.time()
        try:
            logger.debug(f"[EPHEMERAL-{self.id}] Spawn: {self.intent.value}")
            result_payload = await handler(self.payload)
            duration = (time.time() - start) * 1000
            self.result = EphemeralResult(
                success=True,
                intent=self.intent,
                payload=result_payload,
                duration_ms=duration
            )
            logger.debug(f"[EPHEMERAL-{self.id}] Complete: {duration:.1f}ms")
        except Exception as e:
            duration = (time.time() - start) * 1000
            self.result = EphemeralResult(
                success=False,
                intent=self.intent,
                error=str(e),
                duration_ms=duration
            )
            logger.warning(f"[EPHEMERAL-{self.id}] Failed: {e}")
        finally:
            self.completed = True
        return self.result


class EphemeralAgentPool:
    """
    Pool fuer Ephemeral Agents mit automatischer Garbage Collection.
    """
    def __init__(self, max_concurrent: int = 10, gc_interval: float = 5.0):
        self._agents: dict[str, EphemeralAgent] = {}
        self._max_concurrent = max_concurrent
        self._gc_task: asyncio.Task | None = None
        self._gc_interval = gc_interval
        self._handlers: dict[IntentType, Callable] = {}

    def register_handler(self, intent: IntentType, handler: Callable):
        """Registriert einen Handler fuer einen Intent-Typ."""
        self._handlers[intent] = handler
        logger.info(f"[EPHEMERAL-POOL] Handler registriert: {intent.value}")

    async def spawn(
        self,
        intent: IntentType,
        payload: dict,
        ttl: float = 30.0
    ) -> EphemeralAgent:
        """
        Spawnt einen neuen Ephemeral Agent.
        Wirft Exception wenn Pool voll.
        """
        self._gc_sync()
        
        if len(self._agents) >= self._max_concurrent:
            raise RuntimeError(f"Ephemeral Pool erschoepft ({self._max_concurrent} max)")

        agent = EphemeralAgent(intent=intent, payload=payload, ttl_seconds=ttl)
        self._agents[agent.id] = agent
        logger.debug(f"[EPHEMERAL-POOL] Spawned {agent.id} ({len(self._agents)} aktiv)")
        return agent

    async def execute(self, agent: EphemeralAgent) -> EphemeralResult:
        """
        Fuehrt einen Ephemeral Agent aus (sucht passenden Handler).
        """
        handler = self._handlers.get(agent.intent)
        if not handler:
            agent.completed = True
            agent.result = EphemeralResult(
                success=False,
                intent=agent.intent,
                error=f"Kein Handler fuer Intent: {agent.intent.value}"
            )
            return agent.result
        return await agent.execute(handler)

    async def spawn_and_execute(
        self,
        intent: IntentType,
        payload: dict,
        ttl: float = 30.0
    ) -> EphemeralResult:
        """
        Convenience: Spawnt und fuehrt Agent in einem Schritt aus.
        """
        agent = await self.spawn(intent, payload, ttl)
        return await self.execute(agent)

    def _gc_sync(self):
        """Synchrone Garbage Collection: Entfernt abgelaufene/erledigte Agents."""
        to_remove = [
            gid for gid, g in self._agents.items()
            if g.completed or g.is_expired
        ]
        for gid in to_remove:
            del self._agents[gid]
        if to_remove:
            logger.debug(f"[EPHEMERAL-POOL] GC: {len(to_remove)} Agents entfernt")

    async def start_gc_loop(self):
        """Startet den Garbage Collection Loop (fuer Daemon-Betrieb)."""
        async def _gc_loop():
            while True:
                await asyncio.sleep(self._gc_interval)
                self._gc_sync()
        self._gc_task = asyncio.create_task(_gc_loop())

    async def stop(self):
        """Stoppt den GC Loop und alle Agents."""
        if self._gc_task:
            self._gc_task.cancel()
        self._agents.clear()

    @property
    def active_count(self) -> int:
        return len([g for g in self._agents.values() if not g.completed])

    @property
    def stats(self) -> dict:
        return {
            "active": self.active_count,
            "total": len(self._agents),
            "max": self._max_concurrent,
            "handlers": list(self._handlers.keys())
        }


# Singleton Pool fuer globale Nutzung
_global_pool: EphemeralAgentPool | None = None


def get_ephemeral_pool() -> EphemeralAgentPool:
    """Liefert den globalen Ephemeral Agent Pool (Singleton)."""
    global _global_pool
    if _global_pool is None:
        _global_pool = EphemeralAgentPool()
    return _global_pool


# Backward-Kompatibilitaet
Night-AgentIntent = IntentType
Night-AgentResult = EphemeralResult
Night-AgentAgent = EphemeralAgent
Night-AgentAgentPool = EphemeralAgentPool
get_night_agent_pool = get_ephemeral_pool

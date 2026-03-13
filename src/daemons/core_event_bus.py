# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE Event-Bus Daemon – HA WebSocket Listener.

Verbindet sich per WebSocket mit Home Assistant (Scout),
subscribed auf state_changed Events und routet relevante
Aenderungen an Ephemeral Agents zur Verarbeitung.

Domains: binary_sensor, sensor, device_tracker
Integration: EphemeralAgentPool (spawn_and_execute)
Persistenz: ChromaDB events Collection

Features:
- Cooldown-System: Per-Entity, konfigurierbar pro Domain
- Severity-Levels: CRITICAL / WARNING / INFO mit Nacht-Eskalation
- Sensor-Konfiguration: Whitelist, Device-Class-Mapping, Nacht-Fenster
- TTS-Alert bei CRITICAL Events
- Statistiken/Metrics Property
- Reconnect mit exponentiellem Backoff (PHI-basiert)
"""
from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import aiohttp
from dotenv import load_dotenv
from loguru import logger

load_dotenv("c:/CORE/.env")

HASS_URL = (os.getenv("HASS_URL") or "").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or "").strip()

SUBSCRIBE_DOMAINS = {"binary_sensor", "sensor", "device_tracker"}

PHI = 1.6180339887
RECONNECT_BASE_SEC = 2.0
RECONNECT_MAX_SEC = 120.0

IGNORED_ATTRIBUTES = {"friendly_name", "icon", "entity_picture", "supported_features"}

_TRIVIAL_STATES = {"unknown", "unavailable"}


# ---------------------------------------------------------------------------
# Severity
# ---------------------------------------------------------------------------

class EventSeverity(Enum):
    """Schweregrad eines Sensor-Events."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


# ---------------------------------------------------------------------------
# Sensor-Konfiguration
# ---------------------------------------------------------------------------

_DEFAULT_SEVERITY_RULES: dict[str, EventSeverity] = {
    # binary_sensor device_classes
    "motion": EventSeverity.WARNING,
    "occupancy": EventSeverity.WARNING,
    "door": EventSeverity.WARNING,
    "window": EventSeverity.WARNING,
    "smoke": EventSeverity.CRITICAL,
    "gas": EventSeverity.CRITICAL,
    "moisture": EventSeverity.CRITICAL,
    "tamper": EventSeverity.CRITICAL,
    "vibration": EventSeverity.WARNING,
    "safety": EventSeverity.CRITICAL,
    "problem": EventSeverity.WARNING,
    "connectivity": EventSeverity.INFO,
    "battery": EventSeverity.WARNING,
    "plug": EventSeverity.INFO,
    "light": EventSeverity.INFO,
    "presence": EventSeverity.WARNING,
}

_NIGHT_ESCALATION: dict[EventSeverity, EventSeverity] = {
    EventSeverity.WARNING: EventSeverity.CRITICAL,
    EventSeverity.INFO: EventSeverity.WARNING,
}


@dataclass
class SensorConfig:
    """Konfiguration fuer den Event-Bus Sensor-Filter."""

    cooldown_seconds: dict[str, float] = field(default_factory=lambda: {
        "binary_sensor": 30.0,
        "sensor": 120.0,
        "device_tracker": 60.0,
    })

    severity_rules: dict[str, EventSeverity] = field(
        default_factory=lambda: dict(_DEFAULT_SEVERITY_RULES),
    )

    monitored_entities: set[str] | None = field(default=None)
    """None = alle Entities der SUBSCRIBE_DOMAINS. Set = Whitelist."""

    night_start: int = 22
    night_end: int = 6


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _ws_url() -> str:
    base = HASS_URL.replace("https://", "wss://").replace("http://", "ws://")
    return f"{base}/api/websocket"


def _is_significant(old_state: dict | None, new_state: dict | None) -> bool:
    if not old_state or not new_state:
        return new_state is not None
    old_val = old_state.get("state", "")
    new_val = new_state.get("state", "")
    if old_val == new_val:
        return False
    if new_val in _TRIVIAL_STATES or old_val in _TRIVIAL_STATES:
        return False
    return True


def _build_event_summary(entity_id: str, old_state: dict | None, new_state: dict) -> str:
    old_val = (old_state or {}).get("state", "?")
    new_val = new_state.get("state", "?")
    friendly = new_state.get("attributes", {}).get("friendly_name", entity_id)
    return f"{friendly} ({entity_id}): {old_val} -> {new_val}"


def _is_night(hour: int, start: int, end: int) -> bool:
    """True wenn *hour* im Nacht-Fenster liegt (wrap-around faehig)."""
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end


# ---------------------------------------------------------------------------
# Event-Bus
# ---------------------------------------------------------------------------

class MthoEventBus:
    """WebSocket-basierter HA Event-Bus mit Ephemeral Agent Integration."""

    def __init__(self, config: SensorConfig | None = None):
        self._msg_id = 0
        self._running = False
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._pool = None

        self._config = config or SensorConfig()
        self._cooldowns: dict[str, float] = {}
        self._connected_since: float | None = None

        self._stats_events_total: int = 0
        self._stats_events_by_domain: dict[str, int] = {}
        self._stats_events_by_severity: dict[str, int] = {
            s.value: 0 for s in EventSeverity
        }
        self._stats_ghosts_spawned: int = 0
        self._stats_events_cooldown_blocked: int = 0

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    @property
    def stats(self) -> dict[str, Any]:
        """Aktuelle Metriken des Event-Bus."""
        uptime: float | None = None
        if self._connected_since is not None:
            uptime = round(time.time() - self._connected_since, 1)
        return {
            "events_total": self._stats_events_total,
            "events_by_domain": dict(self._stats_events_by_domain),
            "events_by_severity": dict(self._stats_events_by_severity),
            "ghosts_spawned": self._stats_ghosts_spawned,
            "events_cooldown_blocked": self._stats_events_cooldown_blocked,
            "connection_uptime_sec": uptime,
            "cooldowns_active": len(self._cooldowns),
        }

    # ------------------------------------------------------------------
    # Cooldown
    # ------------------------------------------------------------------

    def _check_cooldown(self, entity_id: str, domain: str) -> bool:
        """True wenn das Event durchgelassen wird, False wenn noch in Cooldown."""
        now = time.time()
        last = self._cooldowns.get(entity_id)
        cooldown = self._config.cooldown_seconds.get(
            domain,
            self._config.cooldown_seconds.get("sensor", 120.0),
        )
        if last is not None and (now - last) < cooldown:
            return False
        self._cooldowns[entity_id] = now
        return True

    # ------------------------------------------------------------------
    # Severity
    # ------------------------------------------------------------------

    def _determine_severity(
        self,
        entity_id: str,
        domain: str,
        new_state: dict,
    ) -> EventSeverity:
        """Bestimmt den Schweregrad basierend auf device_class und Tageszeit."""
        device_class = new_state.get("attributes", {}).get("device_class", "")
        base_severity = self._config.severity_rules.get(
            device_class, EventSeverity.INFO,
        )

        if domain == "device_tracker":
            new_val = new_state.get("state", "")
            if new_val == "not_home":
                base_severity = max(base_severity, EventSeverity.WARNING, key=_severity_rank)

        hour = datetime.now().hour
        if _is_night(hour, self._config.night_start, self._config.night_end):
            base_severity = _NIGHT_ESCALATION.get(base_severity, base_severity)

        return base_severity

    # ------------------------------------------------------------------
    # Internals (Netzwerk)
    # ------------------------------------------------------------------

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def _ensure_pool(self):
        if self._pool is None:
            from src.agents.core_agent import get_ephemeral_pool
            from src.agents.scout_core_handlers import register_all_handlers
            self._pool = get_ephemeral_pool()
            if not self._pool._handlers:
                register_all_handlers(self._pool)
            await self._pool.start_gc_loop()

    async def _authenticate(self, ws: aiohttp.ClientWebSocketResponse) -> bool:
        auth_required = await ws.receive_json()
        if auth_required.get("type") != "auth_required":
            logger.error("[EVENT-BUS] Unerwartete Auth-Nachricht: {}", auth_required)
            return False

        await ws.send_json({"type": "auth", "access_token": HASS_TOKEN})
        auth_result = await ws.receive_json()

        if auth_result.get("type") == "auth_ok":
            logger.info("[EVENT-BUS] Authentifiziert bei HA {}", auth_result.get("ha_version", "?"))
            return True
        logger.error("[EVENT-BUS] Auth fehlgeschlagen: {}", auth_result)
        return False

    async def _subscribe(self, ws: aiohttp.ClientWebSocketResponse):
        sub_id = self._next_id()
        await ws.send_json({
            "id": sub_id,
            "type": "subscribe_events",
            "event_type": "state_changed",
        })
        result = await ws.receive_json()
        if result.get("success"):
            logger.info("[EVENT-BUS] Subscribed auf state_changed (id={})", sub_id)
        else:
            logger.error("[EVENT-BUS] Subscribe fehlgeschlagen: {}", result)

    # ------------------------------------------------------------------
    # Event-Pipeline
    # ------------------------------------------------------------------

    async def _handle_event(self, event_data: dict):
        data = event_data.get("event", {}).get("data", {})
        entity_id: str = data.get("entity_id", "")
        domain = entity_id.split(".")[0] if "." in entity_id else ""

        if domain not in SUBSCRIBE_DOMAINS:
            return

        if (
            self._config.monitored_entities is not None
            and entity_id not in self._config.monitored_entities
        ):
            return

        old_state = data.get("old_state")
        new_state = data.get("new_state")

        if not _is_significant(old_state, new_state):
            return

        if not self._check_cooldown(entity_id, domain):
            self._stats_events_cooldown_blocked += 1
            logger.debug("[EVENT-BUS] Cooldown aktiv fuer {}", entity_id)
            return

        severity = self._determine_severity(entity_id, domain, new_state or {})
        summary = _build_event_summary(entity_id, old_state, new_state)

        self._stats_events_total += 1
        self._stats_events_by_domain[domain] = (
            self._stats_events_by_domain.get(domain, 0) + 1
        )
        self._stats_events_by_severity[severity.value] = (
            self._stats_events_by_severity.get(severity.value, 0) + 1
        )

        logger.info("[EVENT-BUS] [{}] {}", severity.value.upper(), summary)

        await self._persist_event(entity_id, old_state, new_state, summary, severity)

        if severity in (EventSeverity.WARNING, EventSeverity.CRITICAL):
            asyncio.create_task(self._forward_to_oc_brain(entity_id, new_state, summary, severity))

        await self._triage_and_spawn(
            entity_id, domain, old_state, new_state, summary, severity,
        )

    # ------------------------------------------------------------------
    # Persistenz
    # ------------------------------------------------------------------

    async def _persist_event(
        self,
        entity_id: str,
        old_state: dict | None,
        new_state: dict,
        summary: str,
        severity: EventSeverity,
    ):
        try:
            from src.network.chroma_client import add_event_to_chroma
            import uuid

            event_id = f"ha_event_{uuid.uuid4().hex[:12]}"
            event_doc = {
                "entity_id": entity_id,
                "old_state": (old_state or {}).get("state"),
                "new_state": new_state.get("state"),
                "summary": summary,
                "severity": severity.value,
            }
            metadata = {
                "entity_id": entity_id,
                "domain": entity_id.split(".")[0],
                "new_state": new_state.get("state", ""),
                "source": "event_bus",
                "severity": severity.value,
                "timestamp": new_state.get("last_changed", ""),
            }
            await add_event_to_chroma(event_id, event_doc, metadata)
        except Exception as e:
            logger.warning("[EVENT-BUS] ChromaDB persist fehlgeschlagen: {}", e)

    async def _forward_to_oc_brain(
        self,
        entity_id: str,
        new_state: dict,
        summary: str,
        severity: EventSeverity,
    ):
        """Leitet WARNING/CRITICAL Events an OC Brain weiter (async, non-blocking)."""
        try:
            from src.network.openclaw_client import send_message_to_agent_async

            event_data = {
                "entity_id": entity_id,
                "state": new_state.get("state"),
                "summary": summary,
                "severity": severity.value,
                "timestamp": new_state.get("last_changed", ""),
            }
            import json as _json
            formatted_msg = f"[CORE_EVENT] type=HA_{severity.value.upper()}\n{_json.dumps(event_data, ensure_ascii=False, indent=2)}"
            ok, resp = await send_message_to_agent_async(
                text=formatted_msg,
                agent_id="main",
                user="core_event_bus",
                timeout=10.0,
            )
            if ok:
                logger.debug("[EVENT-BUS] OC Brain notified: {}", resp[:100])
            else:
                logger.warning("[EVENT-BUS] OC Brain forward failed: {}", resp)
        except Exception as e:
            logger.warning("[EVENT-BUS] OC Brain forward error: {}", e)

    # ------------------------------------------------------------------
    # Triage + Ephemeral Agent Spawn
    # ------------------------------------------------------------------

    async def _triage_and_spawn(
        self,
        entity_id: str,
        domain: str,
        old_state: dict | None,
        new_state: dict,
        summary: str,
        severity: EventSeverity,
    ):
        if severity == EventSeverity.INFO:
            return

        await self._ensure_pool()

        try:
            from src.agents.core_agent import IntentType

            device_class = (new_state or {}).get("attributes", {}).get("device_class", "")
            context = {
                "source": "event_bus",
                "entity_id": entity_id,
                "domain": domain,
                "device_class": device_class,
                "old_state": (old_state or {}).get("state"),
                "new_state": new_state.get("state"),
                "severity": severity.value,
            }

            reasoning_payload = {
                "text": (
                    f"Sicherheitsevent [{severity.value.upper()}]: {summary}"
                    if severity == EventSeverity.CRITICAL
                    else f"Sensor-Event [{severity.value.upper()}]: {summary}"
                ),
                "context": context,
            }
            result = await self._pool.spawn_and_execute(
                IntentType.DEEP_REASONING, reasoning_payload, ttl=30.0,
            )
            self._stats_ghosts_spawned += 1
            level = "info" if result.success else "warning"
            getattr(logger, level)(
                "[EVENT-BUS] Ephemeral DEEP_REASONING {}: {}ms",
                "OK" if result.success else "FAIL",
                f"{result.duration_ms:.0f}",
            )

            if severity == EventSeverity.CRITICAL:
                friendly = (new_state or {}).get(
                    "attributes", {},
                ).get("friendly_name", entity_id)
                alert_text = _build_tts_alert(friendly, device_class, new_state)
                tts_payload = {
                    "text": alert_text,
                    "context": context,
                }
                tts_result = await self._pool.spawn_and_execute(
                    IntentType.TTS_DISPATCH, tts_payload, ttl=15.0,
                )
                self._stats_ghosts_spawned += 1
                tts_level = "info" if tts_result.success else "warning"
                getattr(logger, tts_level)(
                    "[EVENT-BUS] Ephemeral TTS_DISPATCH {}: {}ms",
                    "OK" if tts_result.success else "FAIL",
                    f"{tts_result.duration_ms:.0f}",
                )

        except Exception as e:
            logger.error("[EVENT-BUS] Ephemeral spawn fehlgeschlagen: {}", e)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def run(self):
        if not HASS_URL or not HASS_TOKEN:
            logger.error("[EVENT-BUS] HASS_URL oder HASS_TOKEN nicht konfiguriert")
            return

        self._running = True
        backoff = RECONNECT_BASE_SEC
        url = _ws_url()
        logger.info("[EVENT-BUS] Starte. Ziel: {}", url)

        while self._running:
            try:
                self._session = aiohttp.ClientSession()
                self._ws = await self._session.ws_connect(url, ssl=False, heartbeat=30)

                if not await self._authenticate(self._ws):
                    raise ConnectionError("Auth fehlgeschlagen")

                await self._subscribe(self._ws)
                backoff = RECONNECT_BASE_SEC
                self._connected_since = time.time()

                async for msg in self._ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        data = json.loads(msg.data)
                        if data.get("type") == "event":
                            await self._handle_event(data)
                    elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        logger.warning("[EVENT-BUS] WebSocket geschlossen/Fehler")
                        break

            except Exception as e:
                logger.error("[EVENT-BUS] Verbindungsfehler: {}. Reconnect in {:.1f}s", e, backoff)

            finally:
                self._connected_since = None
                if self._ws and not self._ws.closed:
                    await self._ws.close()
                if self._session and not self._session.closed:
                    await self._session.close()

            await asyncio.sleep(backoff)
            backoff = min(backoff * PHI, RECONNECT_MAX_SEC)

    async def stop(self):
        self._running = False
        if self._ws and not self._ws.closed:
            await self._ws.close()
        if self._session and not self._session.closed:
            await self._session.close()
        logger.info("[EVENT-BUS] Gestoppt. Stats: {}", self.stats)


# ---------------------------------------------------------------------------
# Modul-Level Helfer
# ---------------------------------------------------------------------------

_SEVERITY_RANK = {
    EventSeverity.INFO: 0,
    EventSeverity.WARNING: 1,
    EventSeverity.CRITICAL: 2,
}


def _severity_rank(s: EventSeverity) -> int:
    return _SEVERITY_RANK.get(s, 0)


def _build_tts_alert(friendly_name: str, device_class: str, new_state: dict) -> str:
    """Baut einen TTS-Alert-Text fuer CRITICAL Events."""
    state_val = (new_state or {}).get("state", "unbekannt")
    dc_label = device_class.replace("_", " ") if device_class else "Sensor"
    return f"Achtung! {dc_label.capitalize()} Alarm: {friendly_name} ist {state_val}."


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

async def start_event_bus(
    config: SensorConfig | None = None,
) -> MthoEventBus:
    """Factory: Startet den Event-Bus als asyncio-Task."""
    bus = MthoEventBus(config=config)
    asyncio.create_task(bus.run())
    return bus


if __name__ == "__main__":
    logging_format = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    logger.remove()
    logger.add(lambda msg: print(msg, end=""), format=logging_format, level="DEBUG")
    bus = MthoEventBus()
    asyncio.run(bus.run())

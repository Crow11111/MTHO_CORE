# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.routes import whatsapp_webhook, ha_webhook, oc_channel, mtho_knowledge, mtho_voice, mtho_events, github_webhook
from src.api.middleware.council_gate import CouncilGateMiddleware

_event_bus = None
_ghost_pool = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """MTHO API Lifecycle: Ghost Pool + Event-Bus Startup/Shutdown."""
    global _event_bus, _ghost_pool

    try:
        from src.agents.scout_ghost_handlers import scout_fusion_init
        _ghost_pool = await scout_fusion_init()
        logger.info("[API] Ghost Agent Pool initialisiert")
    except Exception as exc:
        logger.error("[API] Ghost Pool Init fehlgeschlagen: {} – API laeuft weiter", exc)

    hass_url = (os.getenv("HASS_URL") or "").strip()
    hass_token = (os.getenv("HASS_TOKEN") or "").strip()
    if hass_url and hass_token:
        try:
            from src.daemons.mtho_event_bus import start_event_bus
            _event_bus = await start_event_bus()
            logger.info("[API] Event-Bus gestartet (HASS_URL konfiguriert)")
        except Exception as exc:
            logger.error("[API] Event-Bus Start fehlgeschlagen: {} – API laeuft weiter", exc)
    else:
        logger.info("[API] Event-Bus uebersprungen (HASS_URL/HASS_TOKEN nicht gesetzt)")

    # --- CRADLE (MTHO Sync Relay) ---
    webhook_secret = (os.getenv("MTHO_WEBHOOK_SECRET") or "").strip()
    if webhook_secret:
        try:
            import threading
            import asyncio as _aio
            from aiohttp import web as _aio_web

            def _run_cradle():
                from src.network.mtho_sync_relay import app as cradle_app
                loop = _aio.new_event_loop()
                _aio.set_event_loop(loop)
                loop.run_until_complete(_aio_web.run_app(cradle_app, port=8049, handle_signals=False, print=lambda *a: None))

            _cradle_thread = threading.Thread(target=_run_cradle, daemon=True, name="mtho-cradle")
            _cradle_thread.start()
            logger.info("[API] CRADLE Sync Relay gestartet (Port 8049)")
        except Exception as exc:
            logger.error("[API] CRADLE Start fehlgeschlagen: {} – API laeuft weiter", exc)
    else:
        logger.info("[API] CRADLE uebersprungen (MTHO_WEBHOOK_SECRET nicht gesetzt)")

    yield

    if _event_bus is not None:
        try:
            await _event_bus.stop()
            logger.info("[API] Event-Bus gestoppt")
        except Exception as exc:
            logger.warning("[API] Event-Bus Stop Fehler: {}", exc)

    if _ghost_pool is not None:
        try:
            await _ghost_pool.stop()
            logger.info("[API] Ghost Pool GC gestoppt")
        except Exception as exc:
            logger.warning("[API] Ghost Pool Stop Fehler: {}", exc)


app = FastAPI(
    title="MTHO_CORE API",
    description="Main Backend Interface for MTHO Operations",
    version="1.0.0",
    lifespan=lifespan,
)

# Council Gate: Veto-Middleware für kritische Operationen (DELETE, Config, Token, Backup)
app.add_middleware(CouncilGateMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrierung der Routen (Webhooks + OpenClaw Channel)
app.include_router(whatsapp_webhook.router)
app.include_router(ha_webhook.router)
app.include_router(oc_channel.router)
app.include_router(mtho_knowledge.router)
app.include_router(mtho_voice.router)
app.include_router(mtho_events.router)
app.include_router(github_webhook.router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "MTHO_CORE", "version": "1.0.0"}


@app.get("/status")
def system_status() -> dict:
    """Systemstatus inkl. Event-Bus Metriken."""
    hass_configured = bool(
        (os.getenv("HASS_URL") or "").strip()
        and (os.getenv("HASS_TOKEN") or "").strip()
    )
    bus_stats = _event_bus.stats if _event_bus is not None else None
    return {
        "system": "MTHO_CORE",
        "version": "1.0.0",
        "event_bus": {
            "hass_configured": hass_configured,
            "running": _event_bus is not None,
            "stats": bus_stats,
        },
        "ghost_pool": {
            "active": _ghost_pool is not None,
        },
        "cradle": {
            "enabled": bool((os.getenv("MTHO_WEBHOOK_SECRET") or "").strip()),
            "port": 8049,
        },
    }

if __name__ == "__main__":
    import uvicorn
    # Test-Aufruf lokal (z.B. python -m src.api.main)
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

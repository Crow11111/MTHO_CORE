# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""VPS-Slim: Minimale FastAPI App fuer den VPS mit Failover-Endpoint."""
from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from src.api.auth_webhook import verify_ha_auth

_is_prod = os.getenv("MTHO_ENV", "production").lower() == "production"

app = FastAPI(
    title="MTHO_CORE VPS Slim",
    version="1.0.0",
    docs_url=None if _is_prod else "/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://192.168.178.54"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class ForwardedTextPayload(BaseModel):
    """Payload fuer VPS-Failover (Scout -> VPS bei HA-Ausfall)."""

    text: str = Field(..., min_length=1, max_length=4096)
    context: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Pipeline (sync – via asyncio.to_thread aufgerufen)
# ---------------------------------------------------------------------------

def _forwarded_text_pipeline(text: str) -> str:
    """VPS-Fallback Pipeline: Triage -> HA-Command oder Heavy-Reasoning. Sync."""
    from src.ai.llm_interface import mtho_llm
    from src.network.ha_client import HAClient

    ha_client = HAClient()
    triage = mtho_llm.run_triage(text)

    if triage.intent == "command" or triage.intent in [
        "turn_on", "turn_off", "toggle", "light.turn_on", "light.turn_off",
    ]:
        domain = (
            triage.target_entity.split(".")[0]
            if "." in (triage.target_entity or "")
            else "homeassistant"
        )
        service = triage.action or (
            "turn_on" if "turn_off" not in (triage.intent or "") else "turn_off"
        )
        if triage.intent in ["turn_on", "turn_off", "toggle"]:
            service = triage.intent
        success = ha_client.call_service(
            domain=domain, service=service, entity_id=triage.target_entity or "",
        )
        verb = "ausgeführt" if success else "Fehler bei Befehl"
        return f"Befehl {verb} (VPS-Fallback): {service} auf {triage.target_entity}"

    if triage.intent in ["deep_reasoning", "chat"]:
        sys_prompt = (
            "Du bist Virtual Marc, Kopf des Osmium Councils für MTHO_CORE. "
            "Antworte analytisch, auf Systemik fokussiert."
        )
        try:
            from src.logic_core.context_injector import (
                apply_veto,
                check_semantic_drift,
                inject_context_for_agent,
            )

            context_ctx = inject_context_for_agent(text, n_results=3, format="markdown")
            if context_ctx:
                sys_prompt += "\n\n## Relevanter Kontext (context field)\n" + context_ctx
            reply = mtho_llm.invoke_heavy_reasoning(sys_prompt, text)
            if context_ctx:
                veto = check_semantic_drift(context_ctx, reply)
                if veto.vetoed:
                    apply_veto(veto)
            return reply
        except Exception:
            return mtho_llm.invoke_heavy_reasoning(sys_prompt, text)

    return "[SLM Triage] Unbekannter Intent."


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
async def health() -> Dict[str, str]:
    """Health Check."""
    return {"status": "online", "system": "MTHO_CORE_VPS_SLIM", "version": "1.0.0"}


@app.post("/webhook/forwarded_text")
async def receive_forwarded_text(
    payload: ForwardedTextPayload,
    _auth: None = Depends(verify_ha_auth),
) -> Dict[str, str]:
    """VPS-Failover: Scout leitet Text hierher bei HA-Ausfall."""
    logger.info("Forwarded Text von Scout empfangen (VPS-Slim Fallback)")
    try:
        reply = await asyncio.to_thread(_forwarded_text_pipeline, payload.text)
    except Exception:
        logger.exception("Pipeline-Fehler in VPS-Slim Fallback")
        return {"status": "error", "reply": "Interner Fehler.", "routed": "vps_slim_fallback"}
    return {"status": "ok", "reply": reply, "routed": "vps_slim_fallback"}


# ---------------------------------------------------------------------------
# Standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.vps_slim:app",
        host="0.0.0.0",
        port=int(os.getenv("VPS_SLIM_PORT", "8001")),
        log_level="info",
    )

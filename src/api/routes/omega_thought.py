# ============================================================
# MTHO-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Der zentrale Gedanken-Webhook (Gedankenweb Hub).
Direkter In-Weight Injektionskanal für Telemetrie, Audits und Reflexionen,
die NICHT durch das Smart-Home-Triage-SLM blockiert werden dürfen.
"""

import asyncio
from typing import Optional, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from loguru import logger

from src.api.auth_webhook import verify_ha_auth
from src.ai.llm_interface import mtho_llm
from src.logic_core.takt_gate import check_takt_zero
from src.network.chroma_client import add_wuji_observation

router = APIRouter(prefix="/webhook/omega_thought", tags=["omega-thought"])

class ThoughtPayload(BaseModel):
    """Payload für den Gedanken-Webhook."""
    thought: str
    context: Optional[Dict[str, Any]] = None
    sender: str = "unknown"
    require_response: bool = False

def _heavy_reasoning_sync(sys_prompt: str, user_text: str) -> str:
    from src.logic_core.munin import inject_context_for_agent, check_semantic_drift, apply_veto
    wuji_ctx = inject_context_for_agent(user_text, n_results=3, format="markdown")
    if wuji_ctx:
        sys_prompt += "\n\n## Relevanter Kontext (Wuji-Feld)\n" + wuji_ctx
        
    reply = mtho_llm.invoke_heavy_reasoning(sys_prompt, user_text)
    
    if wuji_ctx:
        veto = check_semantic_drift(wuji_ctx, reply)
        if veto.vetoed:
            apply_veto(veto)
    return reply

@router.post("")
async def receive_thought(
    payload: ThoughtPayload,
    _auth: None = Depends(verify_ha_auth),
):
    """
    Der Injektions-Vektor. Umgeht Triage und erzwingt Speicherung/Reflexion.
    """
    logger.info(f"Gedanken-Injektion empfangen von: {payload.sender}")

    if not await check_takt_zero():
        return {"status": "veto", "reason": "system_instability_takt0"}

    # 1. Injektion in das Langzeitgedächtnis (Wuji-Feld / Vector DB)
    metadata = {}
    if payload.context:
        # Dictionary in flache Struktur für ChromaDB umwandeln
        for k, v in payload.context.items():
            metadata[f"ctx_{k}"] = str(v)
            
    await add_wuji_observation(payload.thought, source=payload.sender, metadata=metadata)
    logger.info(f"Gedanke physisch in wuji_field verankert: {payload.thought[:50]}...")
    
    # 2. Reflexion (falls gewünscht)
    reply = "Gedanke erfolgreich verankert (keine Antwort angefordert)."
    if payload.require_response:
        sys_prompt = "Du bist OMEGA_ATTRACTOR, Kopf des Osmium Councils für MTHO_CORE. Analysiere den folgenden System-Gedanken oder Audit-Request analytisch und tiefgründig. Nutze den mitgelieferten Kontext, um gravitative Dissonanzen zu finden."
        try:
            reply = await asyncio.to_thread(_heavy_reasoning_sync, sys_prompt, payload.thought)
        except Exception as e:
            logger.error(f"Fehler bei Heavy Reasoning im Gedanken-Webhook: {e}")
            reply = await asyncio.to_thread(mtho_llm.invoke_heavy_reasoning, sys_prompt, payload.thought)
    
    return {
        "status": "ok", 
        "reply": reply, 
        "routed": "omega_thought_hub"
    }


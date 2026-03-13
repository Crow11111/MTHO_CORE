# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
FRICTION GUARD (Baryonische Klammer 1).
Implementiert die 'Execution-Heresy-Trap' und den 'Friction-Counter'.

Funktion:
1. Scannt ausgehende LLM-Antworten auf illegale Simulation von Shell-Befehlen (Markdown Code-Blocks ohne Tool-Call).
2. Zaehlt Reibungs-Hits (Friction-Counter) pro Session/Agent.
3. Erzwingt Hard-Fail (406) mit Rebound-Prompt bei Verstoss.
"""

import re
import time
from typing import Callable, Awaitable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

from src.logic_core.crystal_grid_engine import CrystalGridEngine

# --- HERESY PATTERNS ---
# Regex, der typische "Ich tue so als ob"-Befehle in Markdown findet.
# Erlaubt sind JSON-Strukturen (Tool-Calls). Verboten sind Bash/Python-Skripte im Freitext,
# wenn sie so aussehen, als wuerden sie gerade ausgefuehrt.
HERESY_PATTERNS = [
    r"```bash",                      # Bash-Bloecke (egal was drin steht)
    r"```sh",                        # Sh-Bloecke
    r"```powershell",                # PowerShell
    r"```cmd",                       # CMD
    r"os\.system\(",                 # Python os.system im Text
    r"subprocess\.run\(",            # Python subprocess im Text
    r"root@",                        # Simulierter Root-Prompt
]

# Friction-Counter (In-Memory, fuer Production spaeter Redis)
FRICTION_STATE = {
    "hits": 0,
    "last_hit": 0.0,
    "system_temperature": 0.0 # 0.0 (idle) bis 1.0 (Kollaps)
}

class FrictionGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        # Nur auf LLM-Generierungs-Endpunkte anwenden
        if not any(path in request.url.path for path in ["/webhook", "/api/core/knowledge", "/api/oc"]):
            return await call_next(request)

        # Response abfangen
        response = await call_next(request)

        # Nur erfolgreiche Antworten scannen
        if response.status_code != 200:
            return response

        # Body lesen
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        response_text = response_body.decode("utf-8", errors="replace")

        # --- SCANNING ---
        violation_found = False
        violation_reason = ""

        # Harte Pruefung: Gibt es verbotene Muster?
        for pattern in HERESY_PATTERNS:
            # Wir suchen im Raw Text (JSON). Backticks koennen normal drin stehen.
            if re.search(pattern, response_text, re.IGNORECASE):
                # Wir erlauben KEINE Ausnahmen mehr fuer "action" im Text.
                violation_found = True
                violation_reason = f"Simulated Execution detected: {pattern}"
                break

        # Fallback-Check fuer 'rm -rf' in Kombination mit root prompt
        if not violation_found and "rm -rf" in response_text and "root@" in response_text:
             violation_found = True
             violation_reason = "Simulated Root Destructive Command"

        if violation_found:
            # --- HARD FAIL & REBOUND ---
            FRICTION_STATE["hits"] += 1
            FRICTION_STATE["last_hit"] = time.time()
            
            # Temperatur-Erhöhung mit Kristall-Gitter Snapping
            new_temp = min(1.0, FRICTION_STATE["system_temperature"] + 0.1)
            FRICTION_STATE["system_temperature"] = CrystalGridEngine.apply_operator_query(new_temp)

            logger.warning(f"[FRICTION GUARD] {violation_reason} | Hits: {FRICTION_STATE['hits']} | Temp: {FRICTION_STATE['system_temperature']:.2f}")

            rebound_prompt = (
                "SYSTEM_ERROR [406]: EXECUTION_HERESY_DETECTED. "
                "You attempted to simulate an action in text (Markdown/Bash) instead of using a physical Tool-Call. "
                "Text is not reality. Use the JSON tool schema immediately."
            )

            return JSONResponse(
                status_code=406,
                content={
                    "status": "veto",
                    "error": "baryonic_limit_violated",
                    "reason": violation_reason,
                    "rebound_prompt": rebound_prompt
                }
            )

        # Wenn sauber: Body zurueckgeben
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )

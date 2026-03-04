"""
Council Gate – Veto-Middleware für kritische Operationen.

Prüft vor kritischen Routen (DELETE, Config, Token-Rotation, Backup) ob ein Veto
erforderlich ist. Nutzt z_widerstand aus dem State Vector als Schwellwert.
Bei kritischen Operationen: Audit-Log + optional Delay oder X-Council-Confirm.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Veto-Schwellwert: z_widerstand >= INV_PHI → Veto-Modus (Confirmation erforderlich)
try:
    from src.config.atlas_state_vector import INV_PHI
    VETO_THRESHOLD = INV_PHI
except ImportError:
    VETO_THRESHOLD = 0.618

# Pfad-Patterns für kritische Operationen (regex, case-insensitive)
CRITICAL_PATH_PATTERNS = [
    re.compile(r"^/api/config", re.I),
    re.compile(r"^/config", re.I),
    re.compile(r"^/api/token/rotate", re.I),
    re.compile(r"^/api/token/.*rotate", re.I),
    re.compile(r"^/rotate", re.I),
    re.compile(r"^/api/backup", re.I),
    re.compile(r"^/backup", re.I),
]

# HTTP-Methoden die als kritisch gelten
CRITICAL_METHODS = {"DELETE"}

# Header für explizite Council-Bestätigung (optional, Wert egal wenn gesetzt)
CONFIRM_HEADER = "X-Council-Confirm"

logger = logging.getLogger("council_gate")


def _is_critical_request(method: str, path: str) -> bool:
    """Prüft ob der Request eine kritische Operation ist."""
    if method in CRITICAL_METHODS:
        return True
    path_norm = path.split("?")[0].rstrip("/") or "/"
    return any(p.match(path_norm) for p in CRITICAL_PATH_PATTERNS)


def _get_z_widerstand() -> float:
    """Liest z_widerstand aus dem aktuellen State Vector."""
    try:
        from src.config.atlas_state_vector import get_current_state

        state = get_current_state()
        return state.z_widerstand
    except Exception:
        return 0.5  # Default: neutral


def _has_confirmation(request: Request) -> bool:
    """Prüft ob X-Council-Confirm gesetzt ist."""
    return bool(request.headers.get(CONFIRM_HEADER))


class CouncilGateMiddleware(BaseHTTPMiddleware):
    """
    Veto-Middleware: Loggt kritische Operationen, optional Delay oder Confirmation.
    """

    def __init__(
        self,
        app,
        *,
        require_confirm_in_veto_mode: bool = True,
        delay_ms: float | None = None,
    ):
        super().__init__(app)
        self._require_confirm = require_confirm_in_veto_mode
        self._delay_ms = delay_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not _is_critical_request(request.method, request.url.path):
            return await call_next(request)

        z = _get_z_widerstand()
        in_veto_mode = z >= VETO_THRESHOLD
        has_confirm = _has_confirmation(request)

        # Audit-Log (immer bei kritischen Operationen)
        logger.info(
            "council_gate|critical|method=%s path=%s z_widerstand=%.3f veto_mode=%s confirm=%s",
            request.method,
            request.url.path,
            z,
            in_veto_mode,
            has_confirm,
            extra={"audit": "council_gate"},
        )

        # Veto-Modus: Confirmation erforderlich?
        if in_veto_mode and self._require_confirm and not has_confirm:
            logger.warning(
                "council_gate|blocked|path=%s z=%.3f (X-Council-Confirm fehlt)",
                request.url.path,
                z,
                extra={"audit": "council_gate"},
            )
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Kritische Operation erfordert Council-Bestätigung (Header: X-Council-Confirm)",
                    "veto_mode": True,
                    "z_widerstand": round(z, 3),
                },
            )

        # Optional: Delay vor Ausführung (Rate-Limit / Überlegungszeit)
        delay = self._delay_ms
        if delay is None:
            delay = float(os.getenv("COUNCIL_GATE_DELAY_MS", "0"))
        if delay > 0:
            await asyncio.sleep(delay / 1000.0)

        return await call_next(request)

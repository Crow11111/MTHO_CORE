"""HTTP client for CORE /webhook/inject_text with VPS Failover."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import LOGGER, FAILOVER_TIMEOUT

_LOGGER = logging.getLogger(LOGGER)


class MthoApiError(Exception):
    """CORE API error."""


class MthoApiClient:
    """Client for CORE webhook API."""

    def __init__(
        self,
        base_url: str,
        fallback_url: str,
        token: str,
        session: aiohttp.ClientSession,
        timeout: int = 30,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._fallback_url = fallback_url.rstrip("/")
        self._token = token
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._fast_connect_timeout = aiohttp.ClientTimeout(
            total=timeout,
            connect=FAILOVER_TIMEOUT,
            sock_connect=FAILOVER_TIMEOUT
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    async def async_validate(self) -> bool:
        """Validate connection: POST ping to /webhook/inject_text with minimal overhead."""
        validate_timeout = aiohttp.ClientTimeout(total=5.0, connect=FAILOVER_TIMEOUT)
        try:
            async with self._session.post(
                f"{self._base_url}/webhook/inject_text",
                json={"text": "ping"},
                headers=self._headers(),
                timeout=validate_timeout,
            ) as resp:
                return resp.status < 400
        except (aiohttp.ClientError, TimeoutError):
            _LOGGER.warning("CORE: Dreadnought offline. Validating VPS Fallback...")
            try:
                async with self._session.post(
                    f"{self._fallback_url}/webhook/forwarded_text",
                    json={"text": "ping"},
                    headers=self._headers(),
                    timeout=validate_timeout,
                ) as resp:
                    return resp.status < 400
            except Exception:
                return False

    async def async_send_text(self, text: str) -> str:
        """Send text to CORE, rerouting to VPS on connection timeout (Lazy Failover)."""
        payload: dict[str, Any] = {"text": text}
        headers = self._headers()
        
        # 1. SCHRITT: Direkter Request (ohne Ping) an Dreadnought.
        # Timeout greift nur bei Connection-Fehlern (failover_timeout),
        # lässt aber genug 'total' Zeit für die LLM-Generierung.
        try:
            _LOGGER.debug(f"CORE: Sende an lokale Pipeline: {self._base_url}")
            async with self._session.post(
                f"{self._base_url}/webhook/inject_text",
                json=payload,
                headers=headers,
                timeout=self._fast_connect_timeout,
            ) as resp:
                if resp.status == 401:
                    raise MthoApiError("Token ungültig (401)")
                if resp.status >= 400:
                    raise MthoApiError(f"CORE API Fehler: {resp.status}")

                data = await resp.json()
                reply = data.get("reply", "")
                return str(reply) if reply else ""
                
        except (aiohttp.ClientError, TimeoutError, OSError) as err:
            _LOGGER.warning(f"CORE: LOKAL OFFLINE. FEHLER: {err}. SCHWENKE AUF VPS-FALLBACK UM...")

        # 2. SCHRITT: Fallback auf VPS Backbone
        try:
            _LOGGER.debug(f"CORE: Rerouting an VPS Backbone: {self._fallback_url}")
            async with self._session.post(
                f"{self._fallback_url}/webhook/forwarded_text",
                json=payload,
                headers=headers,
                timeout=self._timeout,
            ) as resp:
                if resp.status == 401:
                    raise MthoApiError("Token VPS ungültig (401)")
                if resp.status >= 400:
                    raise MthoApiError(f"VPS Backbone API Fehler: {resp.status}")

                data = await resp.json()
                reply = data.get("reply", "")
                return str(reply) if reply else ""
        except Exception as e:
            _LOGGER.error(f"CORE: KRITISCHER FEHLER - LOKAL UND VPS OFFLINE. {e}")
            raise MthoApiError("Gesamtes CORE-Netzwerk offline (Dreadnought & VPS nicht erreichbar)")

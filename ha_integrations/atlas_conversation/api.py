"""HTTP client for ATLAS /webhook/inject_text."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp

from .const import LOGGER

_LOGGER = logging.getLogger(LOGGER)


class AtlasApiError(Exception):
    """ATLAS API error."""


class AtlasApiClient:
    """Client for ATLAS webhook API."""

    def __init__(
        self,
        base_url: str,
        token: str,
        session: aiohttp.ClientSession,
        timeout: int = 30,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    async def async_validate(self) -> bool:
        """Validate connection: POST ping to /webhook/inject_text."""
        try:
            resp = await self._session.post(
                f"{self._base_url}/webhook/inject_text",
                json={"text": "ping"},
                headers=self._headers(),
                timeout=self._timeout,
            )
            if resp.status == 401:
                _LOGGER.warning("ATLAS: Token ungültig (401)")
                return False
            if resp.status == 503:
                _LOGGER.warning("ATLAS: HA_WEBHOOK_TOKEN nicht konfiguriert (503)")
                return False
            if resp.status >= 400:
                _LOGGER.warning("ATLAS: Validierung fehlgeschlagen: %s", resp.status)
                return False
            return True
        except (aiohttp.ClientError, TimeoutError) as err:
            _LOGGER.warning("ATLAS: Verbindung fehlgeschlagen: %s", err)
            return False

    async def async_send_text(self, text: str) -> str:
        """Send text to ATLAS /webhook/inject_text, return reply."""
        url = f"{self._base_url}/webhook/inject_text"
        payload: dict[str, Any] = {"text": text}

        async with self._session.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=self._timeout,
        ) as resp:
            if resp.status == 401:
                raise AtlasApiError("Token ungültig (401)")
            if resp.status == 503:
                raise AtlasApiError("HA_WEBHOOK_TOKEN nicht konfiguriert (503)")
            if resp.status >= 400:
                raise AtlasApiError(f"ATLAS API Fehler: {resp.status}")

            data = await resp.json()
            reply = data.get("reply", "")
            return str(reply) if reply else ""

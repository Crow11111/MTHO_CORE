"""ATLAS Conversation Agent - AbstractConversationAgent implementation."""
from __future__ import annotations

from typing import Literal

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent

from .api import AtlasApiClient, AtlasApiError
from .const import LOGGER

import logging
_LOGGER = logging.getLogger(LOGGER)


class AtlasConversationAgent(conversation.AbstractConversationAgent):
    """ATLAS Conversation Agent - leitet Text an /webhook/inject_text weiter."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: AtlasApiClient,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.client = client

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return supported languages."""
        return MATCH_ALL

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        """Process user input: send to ATLAS, return reply for TTS."""
        text = (user_input.text or "").strip()
        intent_response = intent.IntentResponse(language=user_input.language)

        if not text:
            intent_response.async_set_speech("Kein Text empfangen.")
            return conversation.ConversationResult(response=intent_response)

        try:
            reply = await self.client.async_send_text(text)
            intent_response.async_set_speech(reply or "Keine Antwort von ATLAS.")
        except AtlasApiError as err:
            _LOGGER.error("ATLAS Agent: %s", err)
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                f"ATLAS nicht erreichbar: {err}",
            )
        except Exception as err:
            _LOGGER.exception("ATLAS Agent: unerwarteter Fehler")
            intent_response.async_set_error(
                intent.IntentResponseErrorCode.UNKNOWN,
                "ATLAS Verbindung fehlgeschlagen. Bitte Logs prüfen.",
            )

        return conversation.ConversationResult(response=intent_response)

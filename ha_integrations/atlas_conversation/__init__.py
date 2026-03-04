"""ATLAS Conversation Agent for Home Assistant Assist Pipeline.

Empfängt transkribierten Text von der Assist-Pipeline, sendet an ATLAS /webhook/inject_text,
gibt Antwort für TTS (Piper) zurück.
"""
from __future__ import annotations

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import intent

from .agent import AtlasConversationAgent
from .api import AtlasApiClient
from .const import DOMAIN, CONF_BASE_URL, CONF_TOKEN, DEFAULT_TIMEOUT


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up ATLAS Conversation from config entry."""
    hass.data.setdefault(DOMAIN, {})

    base_url = entry.data[CONF_BASE_URL].rstrip("/")
    token = entry.data[CONF_TOKEN]
    timeout = entry.options.get("timeout", DEFAULT_TIMEOUT) if entry.options else DEFAULT_TIMEOUT

    session = async_get_clientsession(hass)
    client = AtlasApiClient(
        base_url=base_url,
        token=token,
        session=session,
        timeout=timeout,
    )

    try:
        if not await client.async_validate():
            raise ConfigEntryNotReady("ATLAS API nicht erreichbar oder Token ungültig")
    except Exception as err:
        raise ConfigEntryNotReady(f"ATLAS Verbindung fehlgeschlagen: {err}") from err

    agent = AtlasConversationAgent(hass, entry, client)
    conversation.async_set_agent(hass, entry, agent)
    hass.data[DOMAIN][entry.entry_id] = agent

    entry.async_on_unload(lambda: conversation.async_unset_agent(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload ATLAS Conversation."""
    conversation.async_unset_agent(hass, entry)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

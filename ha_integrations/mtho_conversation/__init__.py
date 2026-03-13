"""CORE Conversation Agent for Home Assistant Assist Pipeline.

Empfängt transkribierten Text von der Assist-Pipeline, sendet an CORE /webhook/inject_text,
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

from .agent import MthoConversationAgent
from .api import MthoApiClient
from .const import DOMAIN, CONF_BASE_URL, CONF_FALLBACK_URL, CONF_TOKEN, DEFAULT_TIMEOUT


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up CORE Conversation from config entry."""
    hass.data.setdefault(DOMAIN, {})

    base_url = entry.data[CONF_BASE_URL].rstrip("/")
    fallback_url = entry.data.get(CONF_FALLBACK_URL, "http://187.77.68.250:8080").rstrip("/")
    token = entry.data[CONF_TOKEN]
    timeout = entry.options.get("timeout", DEFAULT_TIMEOUT) if entry.options else DEFAULT_TIMEOUT

    session = async_get_clientsession(hass)
    client = MthoApiClient(
        base_url=base_url,
        fallback_url=fallback_url,
        token=token,
        session=session,
        timeout=timeout,
    )

    try:
        if not await client.async_validate():
            raise ConfigEntryNotReady("CORE API nicht erreichbar oder Token ungültig")
    except Exception as err:
        raise ConfigEntryNotReady(f"CORE Verbindung fehlgeschlagen: {err}") from err

    agent = MthoConversationAgent(hass, entry, client)
    conversation.async_set_agent(hass, entry, agent)
    hass.data[DOMAIN][entry.entry_id] = agent

    entry.async_on_unload(lambda: conversation.async_unset_agent(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload CORE Conversation."""
    conversation.async_unset_agent(hass, entry)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

"""Config flow for ATLAS Conversation."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AtlasApiClient
from .const import DOMAIN, CONF_BASE_URL, CONF_TOKEN, DEFAULT_TIMEOUT


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_BASE_URL, default="http://192.168.178.110:8000"): str,
        vol.Required(CONF_TOKEN): str,
    }
)


class AtlasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle ATLAS Conversation config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        base_url = user_input[CONF_BASE_URL].rstrip("/")
        token = user_input[CONF_TOKEN].strip()

        for entry in self._async_current_entries(include_ignore=False):
            if entry.data.get(CONF_BASE_URL, "").rstrip("/") == base_url:
                return self.async_abort(reason="already_configured")

        errors = {}
        session = async_get_clientsession(self.hass)
        client = AtlasApiClient(
            base_url=base_url,
            token=token,
            session=session,
            timeout=DEFAULT_TIMEOUT,
        )

        try:
            if not await client.async_validate():
                errors["base"] = "cannot_connect"
        except Exception:
            errors["base"] = "cannot_connect"

        if errors:
            return self.async_show_form(
                step_id="user",
                data_schema=DATA_SCHEMA,
                errors=errors,
            )

        return self.async_create_entry(
            title=f"ATLAS - {base_url}",
            data={
                CONF_BASE_URL: base_url,
                CONF_TOKEN: token,
            },
            options={"timeout": DEFAULT_TIMEOUT},
        )

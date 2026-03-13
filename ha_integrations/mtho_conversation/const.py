"""Constants for CORE Conversation integration."""
from __future__ import annotations

DOMAIN = "core_conversation"
LOGGER = "core_conversation"

CONF_BASE_URL = "base_url"
CONF_FALLBACK_URL = "fallback_url"
CONF_TOKEN = "token"

DEFAULT_TIMEOUT = 30
FAILOVER_TIMEOUT = 1.5  # GQA F2: 1.5 seconds ping timeout before rerouting to VPS

"""
Nexos-API-Anbindung für ATLAS_CORE (unter unserer Kontrolle).
Modell-IDs und baseUrl aus der bestehenden OpenClaw-Instanz übernehmen;
siehe docs/NEXOS_EINBINDUNG.md.
"""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

NEXOS_API_KEY = os.getenv("NEXOS_API_KEY", "").strip().strip('"')
NEXOS_BASE_URL = os.getenv("NEXOS_BASE_URL", "https://api.nexos.ai/v1").rstrip("/")


def is_configured() -> bool:
    """True, wenn NEXOS_API_KEY gesetzt ist."""
    return bool(NEXOS_API_KEY)


# Modell-IDs aus bestehender OpenClaw-Config übernehmen (z. B. nexos/a5a1be3e-...).
# Siehe: python -m src.scripts.check_openclaw_config_vps bzw. openclaw.json im Container.
NEXOS_DEFAULT_MODEL = os.getenv("NEXOS_DEFAULT_MODEL", "")


def get_completion(prompt: str, model: str | None = None, max_tokens: int = 2048) -> str:
    """
    Nexos-Completion aufrufen. Bei 402/429/5xx: Fehlerbehandlung bzw. Fallback
    (siehe docs/NEXOS_EINBINDUNG.md).
    """
    if not NEXOS_API_KEY:
        raise ValueError("NEXOS_API_KEY nicht gesetzt – siehe .env und docs/NEXOS_EINBINDUNG.md")
    # TODO: requests.post zu NEXOS_BASE_URL, Modell aus Config/Env;
    # 402 → Guthaben leer, 429 → Retry/Backoff, 5xx → Fallback
    raise NotImplementedError(
        "Nexos-Modul: Implementierung ausstehend; Modell-IDs und Endpoint aus bestehender OpenClaw openclaw.json übernehmen."
    )

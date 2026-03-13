# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Secrets Loader: Liest .secrets.mth NUR bei explizitem Aufruf.
Wird NICHT automatisch geladen wie .env (kein load_dotenv).
Schuetzt sensible Credentials (Google, persoenliche Keys) vor versehentlichem Zugriff.

Usage:
    from security.secrets_loader import get_secret, list_secret_keys

    email = get_secret("GOOGLE_EMAIL")
    keys = list_secret_keys()
"""
import os
from pathlib import Path

SECRETS_FILE = Path(__file__).parent.parent.parent / ".secrets.mth"

_cache: dict[str, str] | None = None


def _load() -> dict[str, str]:
    global _cache
    if _cache is not None:
        return _cache

    if not SECRETS_FILE.exists():
        print(f"[SECRETS] Datei nicht gefunden: {SECRETS_FILE}")
        _cache = {}
        return _cache

    secrets = {}
    with open(SECRETS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and value:
                    secrets[key] = value

    _cache = secrets
    return _cache


def get_secret(key: str, default: str = "") -> str:
    """Liest einen einzelnen Secret-Wert. Laedt die Datei beim ersten Zugriff."""
    return _load().get(key, default)


def list_secret_keys() -> list[str]:
    """Listet alle verfuegbaren Secret-Keys (ohne Werte)."""
    return list(_load().keys())


def is_configured() -> bool:
    """True wenn .secrets.mth existiert und mindestens einen Key hat."""
    return bool(_load())


def reload():
    """Erzwingt Neuladen der Datei (z.B. nach Aenderung)."""
    global _cache
    _cache = None
    _load()

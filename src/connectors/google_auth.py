# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Google OAuth 2.0 Authentifizierung fuer CORE.

Unterstuetzt:
  - Google Tasks API
  - Google Keep API
  - Google Calendar API (zukuenftig)

Setup-Anleitung:
  1. Google Cloud Console -> APIs & Services -> Credentials
  2. OAuth 2.0 Client ID erstellen (Desktop App)
  3. credentials.json herunterladen
  4. In .secrets.mth den Pfad eintragen: GOOGLE_OAUTH_CREDENTIALS_PATH=...
  5. Beim ersten Aufruf oeffnet sich der Browser fuer die Autorisierung
  6. Token wird in data/google_token.json gespeichert (auto-refresh)

Alternativ: credentials.json direkt nach c:/CORE/data/google_credentials.json legen.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

SCOPES = [
    "https://www.googleapis.com/auth/tasks",
    "https://www.googleapis.com/auth/keep",
    "https://www.googleapis.com/auth/calendar.readonly",
]

TOKEN_PATH = Path(__file__).parent.parent.parent / "data" / "google_token.json"
DEFAULT_CREDENTIALS_PATH = Path(__file__).parent.parent.parent / "data" / "google_credentials.json"


def _get_credentials_path() -> Path:
    try:
        from security.secrets_loader import get_secret
        custom = get_secret("GOOGLE_OAUTH_CREDENTIALS_PATH")
        if custom and Path(custom).exists():
            return Path(custom)
    except ImportError:
        pass

    if DEFAULT_CREDENTIALS_PATH.exists():
        return DEFAULT_CREDENTIALS_PATH

    raise FileNotFoundError(
        f"Google OAuth credentials nicht gefunden.\n"
        f"Erwartet: {DEFAULT_CREDENTIALS_PATH}\n"
        f"Oder in .secrets.mth: GOOGLE_OAUTH_CREDENTIALS_PATH=<pfad>\n"
        f"Download: Google Cloud Console -> APIs & Services -> Credentials -> OAuth 2.0 Client ID -> Download JSON"
    )


def get_google_credentials():
    """Liefert gueltige Google OAuth Credentials (mit auto-refresh)."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        raise ImportError(
            "Google Auth Libraries fehlen. Installieren:\n"
            "  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        )

    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_path = _get_credentials_path()
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print(f"[GoogleAuth] Token gespeichert: {TOKEN_PATH}")

    return creds


def build_service(api_name: str, api_version: str):
    """Baut einen Google API Service Client."""
    from googleapiclient.discovery import build
    creds = get_google_credentials()
    return build(api_name, api_version, credentials=creds)


if __name__ == "__main__":
    print("[GoogleAuth] Teste OAuth-Flow...")
    try:
        creds = get_google_credentials()
        print(f"[GoogleAuth] Erfolgreich! Token gueltig: {creds.valid}")
        print(f"[GoogleAuth] Scopes: {creds.scopes}")
    except FileNotFoundError as e:
        print(f"[GoogleAuth] Setup noetig:\n{e}")
    except ImportError as e:
        print(f"[GoogleAuth] Dependencies fehlen:\n{e}")

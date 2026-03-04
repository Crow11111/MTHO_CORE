#!/usr/bin/env python3
"""Deploy atlas_conversation Integration auf Scout via HA Supervisor API / Samba.

Ziel: ha_integrations/atlas_conversation/ -> /config/custom_components/atlas_conversation/
Methoden: Supervisor API (kein File-Upload), Samba-Share, Fallback: manuelle Anweisung.
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests

# --- Config ---
HASS_URL = (os.getenv("HASS_URL") or os.getenv("HA_URL") or "").strip().rstrip("/")
HASS_TOKEN = (os.getenv("HASS_TOKEN") or os.getenv("HA_TOKEN") or "").strip()
SCOUT_IP = os.getenv("SCOUT_IP", "192.168.178.54").strip()
SAMBA_USER = os.getenv("SAMBA_USER", "root").strip()
SAMBA_PASS = os.getenv("SAMBA_PASS", "").strip()

SOURCE_DIR = PROJECT_ROOT / "ha_integrations" / "atlas_conversation"
TARGET_NAME = "atlas_conversation"

# Addon-Slugs (HA Supervisor)
SLUG_SAMBA = "core_samba"
SLUG_SSH = "core_ssh"
SLUG_VSCODE = "a0d7b954_vscode"

HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)
SESSION.verify = False


def _req(method: str, path: str, **kwargs) -> requests.Response | None:
    url = f"{HASS_URL}{path}" if path.startswith("/") else f"{HASS_URL}/{path}"
    kwargs.setdefault("timeout", 15)
    try:
        return SESSION.request(method, url, **kwargs)
    except Exception as e:
        print(f"[FEHLER] Request {method} {path}: {e}")
        return None


def check_addons() -> dict:
    """GET /api/hassio/addons -> Liste Add-ons, Status Samba/SSH/VSCode."""
    r = _req("GET", "/api/hassio/addons")
    if not r or r.status_code != 200:
        return {"ok": False, "addons": [], "samba": None, "ssh": None, "vscode": None}

    data = r.json()
    addons = data.get("data", {}).get("addons") or data.get("addons") or []

    def find(slug: str) -> dict | None:
        for a in addons:
            if a.get("slug") == slug:
                return a
        return None

    samba = find(SLUG_SAMBA)
    ssh = find(SLUG_SSH)
    vscode = find(SLUG_VSCODE)

    return {
        "ok": True,
        "addons": addons,
        "samba": samba,
        "ssh": ssh,
        "vscode": vscode,
    }


def copy_via_unc(local: Path, unc_base: str) -> bool:
    """Kopiert via UNC-Pfad (Windows, bereits gemappt oder Guest)."""
    target = f"{unc_base}\\custom_components\\{TARGET_NAME}"
    try:
        if Path(target).exists():
            shutil.rmtree(target)
        shutil.copytree(str(local), target)
        print(f"[OK] Kopiert via UNC: {target}")
        return True
    except Exception as e:
        print(f"[WARN] UNC-Kopie fehlgeschlagen: {e}")
        return False


def copy_via_smb(local: Path, host: str, share: str) -> bool:
    """Kopiert via smbprotocol (SMB-Credentials)."""
    try:
        from smbclient import register_session, open_file, mkdir
    except ImportError:
        print("[INFO] smbprotocol nicht installiert. pip install smbprotocol")
        return False

    if not SAMBA_PASS:
        print("[WARN] SAMBA_PASS in .env fehlt - Samba-Auth nicht moeglich.")
        return False

    try:
        register_session(host, username=SAMBA_USER, password=SAMBA_PASS)
    except Exception as e:
        print(f"[FEHLER] Samba-Registrierung: {e}")
        return False

    base = f"\\\\{host}\\{share}\\custom_components"
    target_dir = f"{base}\\{TARGET_NAME}"

    def _copy_recursive(src: Path, dst_prefix: str):
        for p in sorted(src.iterdir(), key=lambda x: (x.is_file(), x.name)):
            rel = p.relative_to(src)
            dst_path = f"{dst_prefix}\\{rel}"
            if p.is_dir():
                try:
                    mkdir(dst_path)
                except OSError:
                    pass
                _copy_recursive(p, dst_path)
            else:
                with open(p, "rb") as f_in:
                    with open_file(dst_path, mode="wb") as f_out:
                        f_out.write(f_in.read())

    try:
        try:
            mkdir(base)
        except OSError:
            pass
        try:
            mkdir(target_dir)
        except OSError:
            pass
        _copy_recursive(local, target_dir)
        print(f"[OK] Kopiert via SMB: {target_dir}")
        return True
    except Exception as e:
        print(f"[FEHLER] SMB-Kopie: {e}")
        return False


def deploy() -> tuple[bool, str]:
    """
    Führt Deployment durch. Rückgabe: (erfolg, methode).
    """
    if not SOURCE_DIR.is_dir():
        return False, "SOURCE_DIR fehlt"

    if not HASS_URL or not HASS_TOKEN:
        return False, "HASS_URL/HASS_TOKEN in .env setzen"

    # 1. Addons prüfen
    info = check_addons()
    if not info["ok"]:
        return False, "Supervisor API nicht erreichbar - HASS_URL/Token pruefen"

    samba = info["samba"]
    samba_running = samba and samba.get("state") == "started"

    # 2. Methode: UNC (Windows, Share bereits erreichbar)
    for share in ("config", "homeassistant"):
        unc = f"\\\\{SCOUT_IP}\\{share}"
        if copy_via_unc(SOURCE_DIR, unc):
            return True, f"UNC ({share})"

    # 3. Methode: SMB mit Credentials (wenn Samba aktiv)
    if samba_running:
        for share in ("config", "homeassistant"):
            if copy_via_smb(SOURCE_DIR, SCOUT_IP, share):
                return True, f"SMB ({share})"

    # 4. Fallback: Manuelle Anweisung
    return False, "MANUELL"


def main() -> int:
    print("=== ATLAS: atlas_conversation Integration Deploy auf Scout ===\n")

    info = check_addons()
    if info["ok"]:
        for name, addon in [("Samba", info["samba"]), ("SSH", info["ssh"]), ("VSCode", info["vscode"])]:
            state = addon.get("state", "?") if addon else "nicht installiert"
            print(f"  {name}: {state}")
    else:
        print("  Supervisor API: nicht erreichbar (HASS_URL/Token/Netzwerk pruefen)")
    print()

    success, method = deploy()

    if success:
        print("\n" + "=" * 50)
        print("BEREIT FUER HA NEUSTART")
        print("=" * 50)
        print("Methode:", method)
        print("\nNaechste Schritte:")
        print("  1. Einstellungen -> System -> Home Assistant Core neu starten")
        print("  2. Einstellungen -> Geraete & Dienste -> Integration hinzufuegen")
        print("     -> 'ATLAS Conversation' suchen und konfigurieren")
        print("  3. Telemetrie (optional):")
        print("     tail -f /config/home-assistant.log | grep atlas_conversation")
        print("     (via SSH Add-on oder Log-Viewer)")
        return 0

    # Manuelle Anweisung
    print("\n" + "=" * 50)
    print("MANUELLE DEPLOYMENT-ANWEISUNG")
    print("=" * 50)

    samba = check_addons().get("samba")
    vscode = check_addons().get("vscode")
    samba_running = samba and samba.get("state") == "started"
    vscode_running = vscode and vscode.get("state") == "started"

    if samba_running:
        print("\nSamba Add-on ist aktiv.")
        print("1. Windows: Explorer -> \\\\192.168.178.54\\config (oder \\homeassistant)")
        print("2. Ordner custom_components erstellen, falls nicht vorhanden")
        print("3. Kopiere:")
        print(f"   {SOURCE_DIR}")
        print("   nach: \\\\192.168.178.54\\config\\custom_components\\atlas_conversation")
    elif vscode_running:
        print("\nStudio Code Server Add-on ist aktiv.")
        print("1. Oeffne VSCode ueber HA Add-on (Ingress)")
        print("2. Oeffne Ordner /config")
        print("3. Erstelle custom_components/atlas_conversation falls noetig")
        print("4. Lade Dateien aus ha_integrations/atlas_conversation hoch")
    else:
        print("\nWeder Samba noch VSCode Add-on aktiv.")
        print("Option A: Samba Add-on installieren und starten")
        print("Option B: SSH Add-on nutzen: scp -r ha_integrations/atlas_conversation root@192.168.178.54:/config/custom_components/")

    print("\nNach dem Kopieren:")
    print("  Einstellungen -> System -> Home Assistant Core neu starten")
    return 1


if __name__ == "__main__":
    sys.exit(main())

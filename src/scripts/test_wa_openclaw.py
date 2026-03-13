# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Test: Erreichbarkeit des OpenClaw-Gateways (Hostinger).
Nutzt openclaw_client.check_gateway() – send_message ist im Client noch nicht implementiert;
dieser Test prüft, ob das Gateway erreichbar ist und den Token akzeptiert.
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from src.network.openclaw_client import check_gateway, is_configured


def main():
    if not is_configured():
        print("OpenClaw nicht konfiguriert (VPS_HOST, OPENCLAW_GATEWAY_TOKEN in .env).")
        return 1
    ok, msg = check_gateway(timeout=10.0)
    print(f"OpenClaw Gateway: {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

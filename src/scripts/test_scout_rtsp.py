# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
RTSP-Konnektivitätstest für Scout-MX.
Prüft, ob der RTSP-Stream auf dem Scout erreichbar ist.
"""
import os
import sys
import socket
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

def check_rtsp_port(host, port=8554):
    """Einfacher Socket-Check auf den RTSP-Port."""
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception as e:
        logger.error(f"Fehler beim Port-Check: {e}")
        return False

def main():
    scout_ip = os.getenv("SCOUT_IP", "192.168.178.54")
    rtsp_port = 8554
    stream_name = "mx_brio"
    
    logger.info(f"Prüfe RTSP-Server auf {scout_ip}:{rtsp_port}...")
    
    if check_rtsp_port(scout_ip, rtsp_port):
        logger.info(f"ERFOLG: RTSP-Port {rtsp_port} ist offen.")
        print(f"Beweis: RTSP-Server auf {scout_ip} aktiv. Stream: rtsp://{scout_ip}:{rtsp_port}/{stream_name}")
        return 0
    else:
        logger.error(f"FAIL: RTSP-Port {rtsp_port} auf {scout_ip} nicht erreichbar.")
        print(f"Blocker: go2rtc auf dem Scout läuft nicht oder Port {rtsp_port} ist blockiert.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

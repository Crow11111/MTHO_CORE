"""
ATLAS Health Check: Prueft alle Dienste und gibt JSON-Status zurueck.
"""
import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY", r"c:\ATLAS_CORE\.ssh\id_ed25519_hostinger")
VPS_USER = os.getenv("VPS_USER", "root")
SCOUT_IP = os.getenv("SCOUT_IP", "192.168.178.54")


def _tcp_check(host: str, port: int, timeout: float = 5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


def _ssh_check() -> tuple[bool, str]:
    try:
        r = subprocess.run(
            ["ssh", "-i", VPS_SSH_KEY, "-o", "ConnectTimeout=8",
             "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
             f"{VPS_USER}@{VPS_HOST}", "echo OK"],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0, r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return False, str(e)


def _docker_containers() -> tuple[bool, list[str]]:
    try:
        r = subprocess.run(
            ["ssh", "-i", VPS_SSH_KEY, "-o", "ConnectTimeout=8",
             "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
             f"{VPS_USER}@{VPS_HOST}",
             "docker ps --format '{{.Names}} {{.Status}}'"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode == 0:
            lines = [l.strip() for l in r.stdout.strip().split("\n") if l.strip()]
            return True, lines
        return False, []
    except Exception:
        return False, []


def _http_check(url: str, timeout: float = 5.0) -> bool:
    try:
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status < 500
    except Exception:
        return False


def run_health_check() -> dict:
    results = {"timestamp": datetime.now().isoformat(), "services": {}}
    s = results["services"]

    ssh_ok, ssh_msg = _ssh_check()
    s["vps_ssh"] = {"ok": ssh_ok, "detail": ssh_msg}

    if ssh_ok:
        docker_ok, containers = _docker_containers()
        s["vps_docker"] = {"ok": docker_ok, "containers": containers}
    else:
        s["vps_docker"] = {"ok": False, "detail": "SSH nicht verfuegbar"}

    s["vps_chromadb_8000"] = {"ok": _tcp_check(VPS_HOST, 8000)}
    s["atlas_api_local"] = {"ok": _tcp_check("127.0.0.1", 8000)}
    s["ha_scout"] = {"ok": _http_check(f"https://{SCOUT_IP}:8123")}
    s["ha_vps"] = {"ok": _tcp_check(VPS_HOST, 18123)}

    oc_ok = _tcp_check(VPS_HOST, 18790)
    s["openclaw_spine"] = {"ok": oc_ok}

    s["ollama_local"] = {"ok": _tcp_check("127.0.0.1", 11434)}

    ok_count = sum(1 for v in s.values() if v.get("ok"))
    total = len(s)
    results["summary"] = f"{ok_count}/{total} Dienste OK"
    results["healthy"] = ok_count == total

    return results


if __name__ == "__main__":
    result = run_health_check()
    print(json.dumps(result, indent=2, ensure_ascii=False))

    ok = sum(1 for v in result["services"].values() if v.get("ok"))
    total = len(result["services"])
    if ok < total:
        failed = [k for k, v in result["services"].items() if not v.get("ok")]
        logger.warning(f"ACHTUNG: {total - ok} Dienste offline: {', '.join(failed)}")
        sys.exit(1)
    else:
        logger.success(f"Alle {total} Dienste OK")

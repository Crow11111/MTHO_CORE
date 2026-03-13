# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Minimales VPS-Deploy: SCP von src/ und Dockerfile.vps, SSH docker build/run.
Konfiguration via VPS_HOST, VPS_USER, VPS_DEPLOY_PATH (optional VPS_SSH_KEY).
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

VPS_HOST = os.getenv("VPS_HOST", "").strip() or "core-vps"
VPS_USER = os.getenv("VPS_USER", "root").strip()
VPS_DEPLOY_PATH = os.getenv("VPS_DEPLOY_PATH", "/opt/core-core").strip()
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY", "").strip()


def _ssh_base() -> list[str]:
    base = ["ssh", "-o", "ConnectTimeout=15", "-o", "StrictHostKeyChecking=no"]
    if VPS_SSH_KEY and Path(VPS_SSH_KEY).expanduser().exists():
        base.extend(["-i", str(Path(VPS_SSH_KEY).expanduser())])
    base.append(f"{VPS_USER}@{VPS_HOST}")
    return base


def _scp_base() -> list[str]:
    base = ["scp", "-o", "ConnectTimeout=15", "-o", "StrictHostKeyChecking=no"]
    if VPS_SSH_KEY and Path(VPS_SSH_KEY).expanduser().exists():
        base.extend(["-i", str(Path(VPS_SSH_KEY).expanduser())])
    return base


def _run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    logger.debug("$ {}", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _check(result: subprocess.CompletedProcess[str], msg: str) -> None:
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        logger.error("{}: {}", msg, err[:500])
        sys.exit(1)


def main() -> None:
    logger.info("Deploy VPS Slim → {}@{}:{}", VPS_USER, VPS_HOST, VPS_DEPLOY_PATH)

    # 1. Remote-Verzeichnis anlegen
    r = _run(_ssh_base() + [f"mkdir -p {VPS_DEPLOY_PATH}/docker/agi-state"])
    _check(r, "SSH mkdir fehlgeschlagen")

    # 2. SCP .env (falls vorhanden)
    env_local = PROJECT_ROOT / ".env"
    if env_local.exists():
        r = _run(_scp_base() + [str(env_local), f"{VPS_USER}@{VPS_HOST}:{VPS_DEPLOY_PATH}/.env"])
        _check(r, "SCP .env fehlgeschlagen")
        logger.info("SCP .env OK")

    # 3. SCP src/
    src_local = PROJECT_ROOT / "src"
    if not src_local.is_dir():
        logger.error("src/ nicht gefunden: {}", src_local)
        sys.exit(1)
    r = _run(
        _scp_base() + ["-r", str(src_local), f"{VPS_USER}@{VPS_HOST}:{VPS_DEPLOY_PATH}/"],
        timeout=120,
    )
    _check(r, "SCP src/ fehlgeschlagen")
    logger.info("SCP src/ OK")

    # 4. SCP Dockerfile.vps
    df = PROJECT_ROOT / "docker" / "agi-state" / "Dockerfile.vps"
    if not df.exists():
        logger.error("Dockerfile.vps nicht gefunden: {}", df)
        sys.exit(1)
    r = _run(
        _scp_base() + [str(df), f"{VPS_USER}@{VPS_HOST}:{VPS_DEPLOY_PATH}/docker/agi-state/"],
        timeout=60,
    )
    _check(r, "SCP Dockerfile.vps fehlgeschlagen")
    logger.info("SCP Dockerfile.vps OK")

    # 5. SSH: docker build + run
    cmd = (
        f"cd {VPS_DEPLOY_PATH} && "
        "docker build -f docker/agi-state/Dockerfile.vps -t core-vps-slim . && "
        "docker stop core-vps-slim 2>/dev/null || true && "
        "docker rm core-vps-slim 2>/dev/null || true && "
        "docker run -d --name core-vps-slim --env-file .env -p 8001:8001 core-vps-slim"
    )
    r = _run(_ssh_base() + [cmd], timeout=300)
    _check(r, "SSH docker build/run fehlgeschlagen")
    logger.success("Deploy abgeschlossen: core-vps-slim auf Port 8001")


if __name__ == "__main__":
    main()

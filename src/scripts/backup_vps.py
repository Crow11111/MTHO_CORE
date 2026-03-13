# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
VPS Backup: ChromaDB + PostgreSQL Dumps via SSH.
Loescht lokale Backups > 7 Tage automatisch.
"""
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

VPS_HOST = os.getenv("VPS_HOST", "187.77.68.250")
VPS_USER = os.getenv("VPS_USER", "root")
VPS_SSH_KEY = os.getenv("VPS_SSH_KEY", r"c:\CORE\.ssh\id_ed25519_hostinger")
BACKUP_DIR = Path("c:/CORE/backups/vps")
RETENTION_DAYS = 7


def _ssh(cmd: str, timeout: int = 120) -> tuple[bool, str]:
    full = [
        "ssh", "-i", VPS_SSH_KEY,
        "-o", "ConnectTimeout=10",
        "-o", "StrictHostKeyChecking=no",
        "-o", "BatchMode=yes",
        f"{VPS_USER}@{VPS_HOST}",
        cmd,
    ]
    try:
        r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0:
            return True, r.stdout.strip()
        return False, r.stderr.strip() or r.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "SSH timeout"
    except Exception as e:
        return False, str(e)


def _scp(remote_path: str, local_path: Path, timeout: int = 120) -> bool:
    full = [
        "scp", "-i", VPS_SSH_KEY,
        "-o", "ConnectTimeout=10",
        "-o", "StrictHostKeyChecking=no",
        f"{VPS_USER}@{VPS_HOST}:{remote_path}",
        str(local_path),
    ]
    try:
        r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0
    except Exception as e:
        logger.error(f"SCP Fehler: {e}")
        return False


def backup_chromadb() -> bool:
    logger.info("ChromaDB Backup starten...")
    ok, out = _ssh(
        "docker exec core_chroma_state sh -c "
        "'cd / && tar czf /tmp/chroma_backup.tar.gz chroma/chroma 2>/dev/null'"
    )
    if not ok:
        logger.error(f"ChromaDB tar fehlgeschlagen: {out}")
        return False

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    local = BACKUP_DIR / f"chroma_{ts}.tar.gz"
    if _scp("/tmp/chroma_backup.tar.gz", local):
        logger.success(f"ChromaDB Backup: {local} ({local.stat().st_size / 1024:.0f} KB)")
        _ssh("rm -f /tmp/chroma_backup.tar.gz")
        return True
    logger.error("ChromaDB SCP fehlgeschlagen")
    return False


def backup_postgres() -> bool:
    logger.info("PostgreSQL Backup starten...")
    ok, out = _ssh(
        "docker exec core_postgres_state "
        "pg_dump -U postgres core_state > /tmp/pg_backup.sql 2>/dev/null"
    )
    if not ok:
        logger.error(f"PostgreSQL dump fehlgeschlagen: {out}")
        return False

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    local = BACKUP_DIR / f"postgres_{ts}.sql"
    if _scp("/tmp/pg_backup.sql", local):
        logger.success(f"PostgreSQL Backup: {local} ({local.stat().st_size / 1024:.0f} KB)")
        _ssh("rm -f /tmp/pg_backup.sql")
        return True
    logger.error("PostgreSQL SCP fehlgeschlagen")
    return False


def cleanup_old_backups():
    cutoff = datetime.now() - timedelta(days=RETENTION_DAYS)
    removed = 0
    for f in BACKUP_DIR.glob("*"):
        if f.is_file() and datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
            f.unlink()
            removed += 1
    if removed:
        logger.info(f"{removed} alte Backups entfernt (>{RETENTION_DAYS} Tage)")


def run_backup():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    results["chromadb"] = backup_chromadb()
    results["postgres"] = backup_postgres()
    cleanup_old_backups()

    ok_count = sum(1 for v in results.values() if v)
    logger.info(f"Backup abgeschlossen: {ok_count}/{len(results)} erfolgreich")
    return results


if __name__ == "__main__":
    run_backup()

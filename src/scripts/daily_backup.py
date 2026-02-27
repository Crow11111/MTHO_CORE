"""
Tägliches Backup für ATLAS_CORE → Hostinger-VPS (/var/backups/atlas).

- Archiv: Code (ohne .git, __pycache__, venv, data/backups, logs), config/, data/argos_db/
- .env nur verschlüsselt (Fernet), wenn BACKUP_ENCRYPTION_KEY gesetzt
- Upload per SFTP (paramiko); Retention auf dem VPS (7 Tage)
- Logging: logs/backup.log
- Optional: HEALTHCHECK_URL bei Erfolg aufrufen

.env: VPS_HOST, VPS_USER, VPS_PASSWORD; optional BACKUP_ENCRYPTION_KEY, BACKUP_RETENTION_DAYS, HEALTHCHECK_URL
Siehe docs/BACKUP_PLAN_FINAL.md.
"""
from __future__ import annotations

import io
import logging
import os
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Konfiguration
VPS_HOST = os.getenv("VPS_HOST", "").strip()
VPS_USER = os.getenv("VPS_USER", "root").strip()
VPS_PASSWORD = (os.getenv("VPS_PASSWORD") or "").strip().strip('"').strip("'")
VPS_SSH_KEY = (os.getenv("VPS_SSH_KEY") or "").strip()
VPS_PORT = int(os.getenv("VPS_SSH_PORT", "22"))
REMOTE_BACKUP_DIR = "/var/backups/atlas"
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "7"))
BACKUP_ENCRYPTION_KEY = (os.getenv("BACKUP_ENCRYPTION_KEY") or "").strip()
HEALTHCHECK_URL = (os.getenv("HEALTHCHECK_URL") or "").strip()

# Ausschlüsse beim Archivieren (relativ zu PROJECT_ROOT)
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", "data/backups", "logs", ".cursor"}
EXCLUDE_SUFFIXES = (".pyc", ".pyo", ".log")

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "backup.log"


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def should_exclude(path: Path, arcname: str) -> bool:
    if any(part in EXCLUDE_DIRS for part in Path(arcname).parts):
        return True
    # data/ nur argos_db sichern (laut BACKUP_PLAN_FINAL), Rest auslassen
    an = arcname.replace("\\", "/")
    if an.startswith("data/") and not an.startswith("data/argos_db/"):
        return True
    if path.is_file() and (path.suffix in EXCLUDE_SUFFIXES or ".env" == path.name):
        return True  # .env wird separat verschlüsselt hinzugefügt
    return False


def encrypt_env(env_path: Path, key_encoded: str) -> bytes | None:
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logging.warning("cryptography nicht installiert – .env wird nicht ins Backup aufgenommen.")
        return None
    key_str = key_encoded.strip()
    try:
        fernet = Fernet(key_str.encode("utf-8"))
    except Exception:
        logging.warning("BACKUP_ENCRYPTION_KEY ungültig (erwartet: Fernet.generate_key()) – .env wird übersprungen.")
        return None
    try:
        return fernet.encrypt(env_path.read_bytes())
    except Exception as e:
        logging.warning("Verschlüsselung .env fehlgeschlagen: %s", e)
        return None


def main() -> int:
    setup_logging()
    logger = logging.getLogger()

    if not VPS_HOST or not VPS_USER:
        logger.error("VPS_HOST oder VPS_USER in .env fehlt – Backup abgebrochen.")
        return 1

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    archive_name = f"atlas_backup_{timestamp}.tar.gz"

    try:
        import paramiko
    except ImportError:
        logger.error("paramiko nicht installiert.")
        return 1

    # 1) Archiv erstellen
    logger.info("Erstelle Archiv %s ...", archive_name)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for item in PROJECT_ROOT.rglob("*"):
            if not item.is_file():
                continue
            try:
                arcname = str(item.relative_to(PROJECT_ROOT)).replace("\\", "/")
            except ValueError:
                continue
            if should_exclude(item, arcname):
                continue
            tar.add(item, arcname=arcname)
        # .env verschlüsselt als .env.enc im Archiv
        env_path = PROJECT_ROOT / ".env"
        if BACKUP_ENCRYPTION_KEY and env_path.is_file():
            encrypted = encrypt_env(env_path, BACKUP_ENCRYPTION_KEY)
            if encrypted:
                ti = tarfile.TarInfo(name=".env.enc")
                ti.size = len(encrypted)
                tar.addfile(ti, io.BytesIO(encrypted))
                logger.info(".env verschlüsselt ins Archiv aufgenommen.")
        elif env_path.is_file() and not BACKUP_ENCRYPTION_KEY:
            logger.warning(".env wird nicht gesichert (BACKUP_ENCRYPTION_KEY nicht gesetzt).")

    buf.seek(0)
    archive_bytes = buf.getvalue()
    logger.info("Archiv erstellt: %d Bytes", len(archive_bytes))

    # 2) Verbindung zum VPS
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if VPS_SSH_KEY and os.path.isfile(VPS_SSH_KEY):
            ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, key_filename=VPS_SSH_KEY, timeout=30)
        else:
            ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASSWORD or None, timeout=30)
    except Exception as e:
        logger.error("SSH-Verbindung fehlgeschlagen: %s", e)
        return 1

    try:
        sftp = ssh.open_sftp()
        try:
            try:
                sftp.stat(REMOTE_BACKUP_DIR)
            except FileNotFoundError:
                sftp.mkdir(REMOTE_BACKUP_DIR)
            remote_path = f"{REMOTE_BACKUP_DIR}/{archive_name}"
            with sftp.file(remote_path, "wb") as f:
                f.write(archive_bytes)
            logger.info("Upload: %s -> %s", archive_name, remote_path)
        finally:
            sftp.close()

        # 3) Retention auf dem VPS
        cmd = f"find {REMOTE_BACKUP_DIR} -maxdepth 1 -type f \\( -name 'atlas_backup_*.tar.gz' -o -name 'atlas_env_*.enc' \\) -mtime +{RETENTION_DAYS} -delete"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
        logger.info("Retention (älter als %d Tage) auf VPS ausgeführt.", RETENTION_DAYS)

    finally:
        ssh.close()

    # 4) Optional: Healthcheck
    if HEALTHCHECK_URL:
        try:
            import urllib.request
            urllib.request.urlopen(HEALTHCHECK_URL, timeout=5)
        except Exception as e:
            logger.warning("Healthcheck-Ping fehlgeschlagen: %s", e)

    logger.info("Backup erfolgreich abgeschlossen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
deploy_agi_state.py - Deployment fuer AGI State Services (PostgreSQL & ChromaDB & AGI-Core)
===========================================================================================
Kopiert docker-compose.yml, Dockerfile und src/ auf den VPS und startet die Container.
"""
from __future__ import annotations
import argparse, os, sys, time, tarfile, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import paramiko
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

ADMIN_HOST = (os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST","")).strip()
ADMIN_PORT = int(os.getenv("OPENCLAW_ADMIN_VPS_SSH_PORT") or os.getenv("VPS_SSH_PORT","22"))
ADMIN_USER = (os.getenv("OPENCLAW_ADMIN_VPS_USER") or os.getenv("VPS_USER","root")).strip()
ADMIN_PASS = (os.getenv("OPENCLAW_ADMIN_VPS_PASSWORD") or os.getenv("VPS_PASSWORD","")).strip()
ADMIN_KEY  = (os.getenv("OPENCLAW_ADMIN_VPS_SSH_KEY") or os.getenv("VPS_SSH_KEY","")).strip()

def connect_ssh(host, port, user, password, key, label=""):
    print(f"\n[SSH] {user}@{host}:{port} ({label}) ...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        if key and os.path.isfile(key):
            ssh.connect(host, port=port, username=user, key_filename=key, timeout=15)
        else:
            ssh.connect(host, port=port, username=user, password=password or None, timeout=15)
        print("  OK")
        return ssh
    except Exception as exc:
        print(f"  FEHLER: {exc}")
        return None

def run(ssh, cmd, check=True, dry=False):
    print(f"  $ {cmd[:100]}{'...' if len(cmd)>100 else ''}")
    if dry: return 0, "", ""
    chan = ssh.get_transport().open_session()
    chan.exec_command(cmd)
    out = chan.recv(65535).decode("utf-8", errors="replace")
    err = chan.recv_stderr(65535).decode("utf-8", errors="replace")
    code = chan.recv_exit_status()
    if code != 0 and check:
        print(f"    exit={code} stderr: {err.strip()[:200] or '(leer)'}")
    return code, out, err

def scp_upload(ssh, local_path, remote_path, dry=False):
    """Kopiert eine lokale Datei per SFTP auf den remote Host."""
    print(f"  [SCP] {local_path} -> {remote_path}")
    if dry: return
    try:
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
    except Exception as exc:
        print(f"  FEHLER beim SCP {local_path} -> {remote_path}: {exc}")
        raise

def scp_upload_tar(ssh, local_dir, remote_dir, dry=False):
    """Verpackt ein lokales Verzeichnis als tar.gz, laedt es hoch und entpackt es remote."""
    print(f"  [TAR-SCP] {local_dir} -> {remote_dir}")
    if dry: return
    
    temp_tar_path = None
    try:
        fd, temp_tar_path = tempfile.mkstemp(suffix=".tar.gz")
        os.close(fd)
        
        print(f"    Erstelle lokales Archiv: {temp_tar_path}...")
        with tarfile.open(temp_tar_path, "w:gz") as tar:
            def filter_function(tarinfo):
                if "__pycache__" in tarinfo.name or ".pyc" in tarinfo.name:
                    return None
                return tarinfo
            
            # arcname stellt sicher, dass das Basis-Verzeichnis (z.B. 'src') im Archiv enthalten ist
            tar.add(local_dir, arcname=os.path.basename(local_dir.rstrip("\\/")), filter=filter_function)
            
        remote_tar_path = f"/tmp/{os.path.basename(temp_tar_path)}"
        print(f"    Upload nach {remote_tar_path}...")
        sftp = ssh.open_sftp()
        sftp.put(temp_tar_path, remote_tar_path)
        sftp.close()
        
        print(f"    Entpacke auf Remote in {remote_dir}...")
        # Das Elternverzeichnis auf dem Server (z.B. /opt/core)
        parent_remote = os.path.dirname(remote_dir.rstrip("/"))
        mkdir(ssh, parent_remote, dry=dry)
        
        run(ssh, f"tar -xzf {remote_tar_path} -C {parent_remote} && rm {remote_tar_path}", check=True, dry=dry)
        
    except Exception as exc:
        print(f"  FEHLER beim TAR-SCP {local_dir} -> {remote_dir}: {exc}")
        raise
    finally:
        if temp_tar_path and os.path.exists(temp_tar_path):
            os.remove(temp_tar_path)

def mkdir(ssh, path, dry=False):
    run(ssh, f"mkdir -p {path}", check=False, dry=dry)

def deploy_agi_state(ssh, dry=False):
    compose_dir = "/opt/core/docker/agi-state"
    core_dir = "/opt/core"
    src_remote = f"{core_dir}/src"
    src_db_dir = f"{src_remote}/db"
    
    mkdir(ssh, compose_dir, dry=dry)
    mkdir(ssh, core_dir, dry=dry)
    
    # Lokale Pfade
    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    compose_local = os.path.join(proj_root, "docker", "agi-state", "docker-compose.yml")
    dockerfile_local = os.path.join(proj_root, "docker", "agi-state", "Dockerfile")
    src_local = os.path.join(proj_root, "src")
    env_local = os.path.join(proj_root, ".env")
    
    compose_remote = f"{compose_dir}/docker-compose.yml"
    dockerfile_remote = f"{compose_dir}/Dockerfile"
    env_remote = f"{core_dir}/.env"
    
    print("\n[1] Upload Dateien & Verzeichnisse per SCP/TAR ...")
    if os.path.exists(compose_local):
        scp_upload(ssh, compose_local, compose_remote, dry=dry)
    else:
        print(f"  FEHLER: Lokale Datei {compose_local} nicht gefunden!")
        
    if os.path.exists(dockerfile_local):
        scp_upload(ssh, dockerfile_local, dockerfile_remote, dry=dry)
    else:
        print(f"  FEHLER: Lokale Datei {dockerfile_local} nicht gefunden!")

    if os.path.exists(env_local):
        scp_upload(ssh, env_local, env_remote, dry=dry)
    else:
        print(f"  WARNUNG: Lokale .env nicht gefunden, erwarte dass sie auf Server existiert.")

    if os.path.exists(src_local):
        scp_upload_tar(ssh, src_local, src_remote, dry=dry)
    else:
        print(f"  FEHLER: Lokales Verzeichnis {src_local} nicht gefunden!")
    
    print("\n[2] Starte Docker Compose ...")
    run(ssh, "docker network inspect core_net >/dev/null 2>&1 || docker network create core_net", check=False, dry=dry)
    # WICHTIG: build VOR up -d
    run(ssh, f"cd {compose_dir} && docker compose pull && docker compose build && docker compose up -d", check=True, dry=dry)
    
    print("\n[3] Init-Prozess abwarten und anstossen ...")
    time.sleep(5)
    run(ssh, "docker ps --format '{{.Names}}' | grep -iE 'postgres_state|chroma_state|agi-core'", check=False, dry=dry)
    
    print("\n  Info: PostgreSQL initialisiert sich automatisch via init_postgres.sql im Entrypoint.")
    print("  Info: Starte init_chroma.py fuer ChromaDB...")
    
    c, out, err = run(ssh, "python3 -c 'import chromadb' 2>/dev/null", check=False, dry=dry)
    if c == 0:
        run(ssh, "cd /opt/core && python3 src/db/init_chroma.py", check=False, dry=dry)
    else:
        print("  'chromadb' fehlt auf Host. Verwende temporaeren Docker-Container...")
        chroma_init_cmd = (
            "docker run --rm --network core_net "
            f"-v {src_db_dir}:/app/db "
            "-e CHROMA_HOST=core_chroma_state "
            "-e CHROMA_PORT=8000 "
            "python:3.10-slim bash -c 'pip install chromadb && python /app/db/init_chroma.py'"
        )
        run(ssh, chroma_init_cmd, check=False, dry=dry)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    if not ADMIN_HOST:
        print("FEHLER: OPENCLAW_ADMIN_VPS_HOST oder VPS_HOST fehlt in .env")
        return 1
        
    ssh = connect_ssh(ADMIN_HOST, ADMIN_PORT, ADMIN_USER, ADMIN_PASS, ADMIN_KEY, "Admin-VPS")
    if not ssh and not args.dry_run:
        return 1
        
    try:
        deploy_agi_state(ssh, dry=args.dry_run)
        print("\nDeployment AGI State erfolgreich abgeschlossen.")
    except Exception as e:
        print(f"\nFEHLER beim Deployment: {e}")
        if ssh: ssh.close()
        return 1
        
    if ssh: ssh.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
Ring-0 VPS-Sync + Abgleich mit programmatischem SSH-Tunnel.
Baut Tunnel zu VPS (Paramiko, .env: VPS_HOST, VPS_USER, VPS_PASSWORD oder VPS_SSH_KEY),
führt sync_core_directives_to_vps und check_oc_brain_chroma_abgleich aus,
gibt Abgleich-Output aus (für Eintrag in VERGLEICHSDOKUMENT Abschnitt 2).
"""
from __future__ import annotations

import os
import sys
import subprocess
import threading
import socket
import select

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

HOST = os.getenv("VPS_HOST", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()

# Lokal 8001, damit Backend (Port 8000) nicht kollidiert
LOCAL_PORT = 8001
REMOTE_HOST, REMOTE_PORT = "127.0.0.1", 8000


def _forward_handler(request, chan, transport, remote_host, remote_port):
    """Kopiert Daten zwischen lokalem Socket und SSH direct-tcpip Channel."""
    try:
        while True:
            r, _, _ = select.select([request, chan], [], [])
            if request in r:
                data = request.recv(1024)
                if not data:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if not data:
                    break
                request.send(data)
    except (socket.error, OSError, EOFError):
        pass
    finally:
        try:
            request.close()
        except Exception:
            pass
        try:
            chan.close()
        except Exception:
            pass


def _run_forward_server(transport, bind_port, remote_host, remote_port):
    """Lokal Port bind_port → remote_host:remote_port über transport."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", bind_port))
    sock.listen(5)
    try:
        while transport.is_active():
            try:
                client, _ = sock.accept()
            except (socket.error, OSError):
                break
            try:
                chan = transport.open_channel(
                    "direct-tcpip", (remote_host, remote_port), client.getpeername()
                )
            except Exception:
                client.close()
                continue
            if chan is None:
                client.close()
                continue
            t = threading.Thread(
                target=_forward_handler,
                args=(client, chan, transport, remote_host, remote_port),
                daemon=True,
            )
            t.start()
    finally:
        try:
            sock.close()
        except Exception:
            pass


def _wait_port(host: str, port: int, timeout_sec: float = 15.0) -> bool:
    """Wartet bis host:port erreichbar ist."""
    import time
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect((host, port))
            s.close()
            return True
        except (socket.error, OSError):
            time.sleep(0.3)
    return False


def _run_sync_and_abgleich(env_sync: dict, env_abgleich: dict) -> int:
    """Führt Sync und Abgleich aus. Gibt 0 bei Erfolg zurück."""
    print("[1/2] Sync core_directives -> VPS ...")
    r = subprocess.run(
        [sys.executable, "-m", "src.scripts.sync_core_directives_to_vps"],
        cwd=PROJECT_ROOT,
        env=env_sync,
        capture_output=True,
        text=True,
        timeout=60,
    )
    print(r.stdout or "")
    if r.stderr:
        print(r.stderr, file=sys.stderr)
        if r.returncode != 0:
            print("Sync fehlgeschlagen. Exit:", r.returncode)
            print("Hinweis: Wenn SSH steht, kann 'Connection refused' heißen: auf dem VPS lauscht kein Dienst auf 127.0.0.1:8000 (ChromaDB starten bzw. Docker-Port prüfen).")
            return 1
    print("\n[2/2] Abgleich (VPS core_directives) ...")
    r2 = subprocess.run(
        [sys.executable, "-m", "src.scripts.check_oc_brain_chroma_abgleich"],
        cwd=PROJECT_ROOT,
        env=env_abgleich,
        capture_output=True,
        text=True,
        timeout=30,
    )
    abgleich_out = (r2.stdout or "") + (r2.stderr or "")
    print(abgleich_out)
    if r2.returncode != 0:
        print("Abgleich-Skript Exit-Code:", r2.returncode)
    return 0


def main() -> int:
    if not HOST or not USER:
        print("FEHLER: VPS_HOST oder VPS_USER in .env fehlt.")
        return 1

    env_sync = os.environ.copy()
    env_sync["CHROMA_VPS_HOST"] = "127.0.0.1"
    env_sync["CHROMA_VPS_PORT"] = str(LOCAL_PORT)
    env_abgleich = os.environ.copy()
    env_abgleich["CHROMA_HOST"] = "127.0.0.1"
    env_abgleich["CHROMA_PORT"] = str(LOCAL_PORT)

    ssh_process = None
    use_paramiko = True

    # 1) Versuch: Paramiko-Tunnel
    try:
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if KEY_PATH and os.path.isfile(KEY_PATH):
            ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
        else:
            ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)
        transport = ssh.get_transport()
        server_thread = threading.Thread(
            target=_run_forward_server,
            args=(transport, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT),
            daemon=True,
        )
        server_thread.start()
        import time
        time.sleep(1.0)
        if not _wait_port("127.0.0.1", LOCAL_PORT, timeout_sec=5.0):
            print("Warnung: Lokaler Port", LOCAL_PORT, "nicht bereit, fahre trotzdem fort.")
        try:
            return _run_sync_and_abgleich(env_sync, env_abgleich)
        finally:
            ssh.close()
    except Exception as e:
        print(f"Paramiko-Tunnel fehlgeschlagen: {e}")
        use_paramiko = False

    # 2) Fallback: System-SSH (Key-Auth; gleicher Pfad wie Test-NetConnection)
    if not use_paramiko:
        print("Fallback: System-SSH (ssh -L ...). Erfordert Key-Auth.")
        ssh_cmd = [
            "ssh", "-L", f"127.0.0.1:{LOCAL_PORT}:{REMOTE_HOST}:{REMOTE_PORT}",
            "-N", "-o", "StrictHostKeyChecking=no", "-o", "BatchMode=yes",
            f"{USER}@{HOST}", "-p", str(PORT),
        ]
        try:
            ssh_process = subprocess.Popen(ssh_cmd, cwd=PROJECT_ROOT)
            if not _wait_port("127.0.0.1", LOCAL_PORT, timeout_sec=12.0):
                if ssh_process:
                    ssh_process.terminate()
                print("FEHLER: Port", LOCAL_PORT, "nach SSH-Start nicht erreichbar. Key-Auth konfiguriert?")
                return 1
            rc = _run_sync_and_abgleich(env_sync, env_abgleich)
            return rc
        except FileNotFoundError:
            print("FEHLER: 'ssh' nicht gefunden (OpenSSH-Client installieren).")
            return 1
        finally:
            if ssh_process and ssh_process.poll() is None:
                ssh_process.terminate()
                try:
                    ssh_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    ssh_process.kill()
    return 1


if __name__ == "__main__":
    sys.exit(main())

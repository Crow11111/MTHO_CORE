# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Stellt den OpenClaw-Container auf Hostinger so um, dass er Google direkt als Provider
akzeptiert. Übergibt den API-Key als Umgebungsvariable GOOGLE_API_KEY und trägt
das explizite Modell gemini-3.1-pro-preview ein.

Aufruf: python -m src.scripts.fix_openclaw_native_google
"""
from __future__ import annotations
import base64, json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("VPS_HOST", "").strip()
USER = os.getenv("VPS_USER", "root")
PASSWORD = os.getenv("VPS_PASSWORD", "")
KEY_PATH = os.getenv("VPS_SSH_KEY", "").strip()
PORT = int(os.getenv("VPS_SSH_PORT", "22"))
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
CONTAINER = "openclaw-ntw5-openclaw-1"
CFG_FILE = "/data/.openclaw/openclaw.json"

def _run(ssh: paramiko.SSHClient, cmd: str) -> tuple[int, str, str]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return code, out, err

def main() -> int:
    if not HOST or not USER or not GEMINI_KEY:
        print("FEHLER: VPS_HOST, VPS_USER oder GEMINI_API_KEY fehlt.")
        return 1

    print("Verbinde mit VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if KEY_PATH and os.path.isfile(KEY_PATH):
        ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
    else:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)

    # 1. Config vorbereiten
    print("Setze Config...")
    code, raw, _ = _run(ssh, f"docker exec {CONTAINER} cat {CFG_FILE} 2>/dev/null")
    try:
        cfg = json.loads(raw) if raw else {}
    except:
        cfg = {}

    cfg.setdefault("models", {}).setdefault("providers", {})
    cfg["models"]["providers"]["google"] = {
        "apiKey": "$GOOGLE_API_KEY",
        "models": [
            {
                "id": "gemini-3.1-pro-preview",
                "name": "Gemini 3.1 Pro",
                "reasoning": True,
                "input": ["text", "image"],
                "contextWindow": 2000000,
                "maxTokens": 8192
            }
        ]
    }
    
    cfg.setdefault("agents", {}).setdefault("defaults", {})
    cfg["agents"]["defaults"]["model"] = {"primary": "google/gemini-3.1-pro-preview"}
    
    agents = cfg["agents"].get("list") or []
    found = False
    for a in agents:
        if isinstance(a, dict) and a.get("id") == "main":
            a["model"] = "google/gemini-3.1-pro-preview"
            found = True
    if not found:
        agents.append({"id": "main", "name": "main", "model": "google/gemini-3.1-pro-preview"})
    cfg["agents"]["list"] = agents

    b64 = base64.standard_b64encode(json.dumps(cfg, indent=2).encode()).decode()
    _run(ssh, f"docker exec {CONTAINER} sh -c 'echo {b64} | base64 -d > {CFG_FILE}'")

    # 2. Container neu bauen/starten mit GOOGLE_API_KEY
    print("Starte Container neu mit GOOGLE_API_KEY...")
    
    # Wir muessen den Container mit dem ENV-Key starten.
    # Da es ein Hostinger-Container ist, gucken wir uns den run-Befehl an und injecten die ENV.
    _run(ssh, f"docker update --env GOOGLE_API_KEY='{GEMINI_KEY}' {CONTAINER}") # docker update erlaubt keine ENVs hinzuzufuegen
    
    # Workaround fuer bestehende Container:
    # Wir holen uns das Image und die Parameter und erstellen ihn neu, ABER
    # da wir den Hostinger-Startprozess nicht zerschiessen wollen, schreiben wir die Env
    # in das Startskript oder profile des Containers, oder wir geben sie bei docker exec mit.
    # Bei OpenClaw greift es oft auf .env im /data/.openclaw/ Verzeichnis zurueck.
    
    env_file = "/data/.openclaw/.env"
    _run(ssh, f"docker exec {CONTAINER} sh -c 'echo GOOGLE_API_KEY={GEMINI_KEY} >> {env_file}'")
    _run(ssh, f"docker restart {CONTAINER}")

    time.sleep(5)
    print("Logs:")
    _, logs, _ = _run(ssh, f"docker logs {CONTAINER} --tail 20")
    print(logs.encode("ascii", "replace").decode("ascii"))
    
    ssh.close()
    print("Fertig.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

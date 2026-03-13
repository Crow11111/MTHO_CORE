# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Korrigiert den google-Provider in /data/.openclaw/openclaw.json mit allen
Pflichtfeldern (baseUrl, models) die OpenClaw erwartet.
Aufruf: python -m src.scripts.fix_openclaw_google_provider
"""
from __future__ import annotations
import base64, json, os, sys, time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import paramiko
from dotenv import load_dotenv
load_dotenv()

HOST = os.getenv("VPS_HOST","").strip()
USER = os.getenv("VPS_USER","root")
PASSWORD = os.getenv("VPS_PASSWORD","")
KEY_PATH = os.getenv("VPS_SSH_KEY","").strip()
PORT = int(os.getenv("VPS_SSH_PORT","22"))
GEMINI_KEY = os.getenv("GEMINI_API_KEY","").strip().strip('"')
CONTAINER = "openclaw-ntw5-openclaw-1"
CFG_FILE  = "/data/.openclaw/openclaw.json"

def _run(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = (stdout.read() or b"").decode("utf-8", errors="replace").strip()
    err = (stderr.read() or b"").decode("utf-8", errors="replace").strip()
    return out, err

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if KEY_PATH and os.path.isfile(KEY_PATH):
        ssh.connect(HOST, port=PORT, username=USER, key_filename=KEY_PATH, timeout=15)
    else:
        ssh.connect(HOST, port=PORT, username=USER, password=PASSWORD or None, timeout=15)

    # Config laden
    out, _ = _run(ssh, f"docker exec {CONTAINER} cat {CFG_FILE} 2>/dev/null")
    cfg = json.loads(out)

    # Google-Provider mit echten API-Modellnamen (OpenAI-kompatibler Endpoint)
    cfg["models"]["providers"]["google"] = {
        "baseUrl": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "apiKey": GEMINI_KEY,
        "auth": "api-key",
        "api": "openai-completions",
        "models": [
            {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash (Google)",
                "reasoning": False,
                "input": ["text", "image"],
                "contextWindow": 1000000,
                "maxTokens": 8192,
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "compat": {
                    "supportsStore": False,
                    "supportsDeveloperRole": False,
                    "supportsReasoningEffort": False,
                }
            },
            {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro (Google)",
                "reasoning": False,
                "input": ["text", "image"],
                "contextWindow": 2000000,
                "maxTokens": 8192,
                "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
                "compat": {
                    "supportsStore": False,
                    "supportsDeveloperRole": False,
                    "supportsReasoningEffort": False,
                }
            }
        ]
    }
    # agents.list auf gemini-2.0-flash setzen
    agents_list = cfg.get("agents", {}).get("list", [])
    for a in agents_list:
        if isinstance(a, dict) and a.get("id") == "main":
            a["model"] = "google/gemini-2.0-flash"
    cfg.setdefault("agents", {})["list"] = agents_list

    payload = json.dumps(cfg, indent=2)
    b64 = base64.standard_b64encode(payload.encode("utf-8")).decode("ascii")
    out2, err2 = _run(ssh, f"docker exec {CONTAINER} sh -c 'echo {b64} | base64 -d > {CFG_FILE}'")
    print(f"Config geschrieben: {out2 or err2 or 'OK'}")

    # Container restart
    out3, _ = _run(ssh, f"docker restart {CONTAINER}")
    print(f"Container neugestartet: {out3}")
    time.sleep(8)

    # Logs prüfen
    out4, _ = _run(ssh, f"docker logs {CONTAINER} --tail 15 2>&1")
    safe = out4.encode("ascii", errors="replace").decode("ascii")
    print(f"\nLogs nach Restart:\n{safe}")
    ssh.close()

if __name__ == "__main__":
    main()

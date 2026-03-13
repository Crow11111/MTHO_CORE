# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import sys
import time
import requests
import json
from dotenv import load_dotenv

# Farben für Output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(step, status, message=""):
    if status == "OK":
        print(f"{step:<40} [{GREEN}LÄUFT{RESET}] {message}")
    elif status == "FAIL":
        print(f"{step:<40} [{RED}LÄUFT NICHT{RESET}] {message}")
    elif status == "WARN":
        print(f"{step:<40} [{YELLOW}WARNUNG{RESET}] {message}")
    else:
        print(f"{step:<40} [{status}] {message}")

def verify_openclaw_setup():
    print(f"\n=== CORE Swarm OpenClaw Verification ===\n")

    # 1. Config laden
    load_dotenv()
    
    # Konfiguration
    VPS_IP = "187.77.68.250" # Fest vorgegeben laut Prompt
    BASE_URL = f"https://{VPS_IP}"
    TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN")
    
    # Z1: Config Validierung
    step = "Z1: Konfiguration laden"
    if not TOKEN:
        print_status(step, "FAIL", "OPENCLAW_GATEWAY_TOKEN fehlt in .env")
        return
    
    # Check if VPS_HOST in env matches (optional warning)
    env_host = os.getenv("OPENCLAW_ADMIN_VPS_HOST") or os.getenv("VPS_HOST")
    if env_host and env_host != VPS_IP:
         print_status(step, "WARN", f"Lokaler VPS_HOST ({env_host}) ungleich Ziel-IP ({VPS_IP})")
    else:
        print_status(step, "OK", f"Token vorhanden. Ziel: {VPS_IP}")

    # Headers für API Calls
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # Z3/Z4: API Call /v1/models
    step = "Z3/Z4: API Check (/v1/models)"
    try:
        # verify=False weil IP-Zertifikate oft self-signed oder Hostname-Mismatch haben
        response = requests.get(
            f"{BASE_URL}/v1/models", 
            headers=headers, 
            timeout=5,
            verify=False 
        )
        
        if response.status_code == 200:
            data = response.json()
            model_count = len(data.get("data", []))
            print_status(step, "OK", f"Status 200. Modelle gefunden: {model_count}")
            # Optional: Liste Modelle
            # print(json.dumps(data, indent=2))
        else:
            print_status(step, "FAIL", f"Status: {response.status_code}. Response: {response.text[:100]}")
            
    except requests.exceptions.Timeout:
        print_status(step, "FAIL", "Timeout nach 5s")
    except requests.exceptions.ConnectionError as e:
        print_status(step, "FAIL", f"Verbindungsfehler: {str(e)}")
    except Exception as e:
        print_status(step, "FAIL", f"Fehler: {str(e)}")

    # Z5: Chat Completion (Agent 'main')
    step = "Z5: Chat Agent 'main'"
    payload = {
        "model": "main",
        "messages": [
            {"role": "user", "content": "Ping. Bist du bereit?"}
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                print_status(step, "OK", f"Antwort erhalten: '{content[:50]}...'")
            else:
                print_status(step, "WARN", "Status 200, aber keine 'choices' in Antwort.")
        else:
            print_status(step, "FAIL", f"Status: {response.status_code}. Response: {response.text[:100]}")
            
    except requests.exceptions.Timeout:
        print_status(step, "FAIL", "Timeout nach 10s")
    except Exception as e:
        print_status(step, "FAIL", f"Fehler: {str(e)}")

    print(f"\n=========================================\n")

if __name__ == "__main__":
    # Suppress InsecureRequestWarning for cleaner output
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    verify_openclaw_setup()

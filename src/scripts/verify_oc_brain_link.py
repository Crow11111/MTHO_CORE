# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import sys
import os
import time

# Root-Pfad hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.network.openclaw_client import send_message_to_agent

def main():
    print("--- OC BRAIN LINK VERIFICATION ---")
    
    # 1. Ping
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    message = f"CORE PING {timestamp}. Status Report anfordern."
    
    print(f"Sending to OC Brain (Agent 'main'): '{message}'")
    
    start = time.time()
    ok, response = send_message_to_agent(message, agent_id="main", timeout=60.0)
    duration = time.time() - start
    
    if ok:
        print(f"SUCCESS ({duration:.2f}s)")
        print(f"Response: {response}")
        
        # Prüfung auf Validität
        if "I am" in response or "Status" in response or len(response) > 5:
             print(">> BRAIN IS ACTIVE AND INTELLIGENT.")
        else:
             print(">> BRAIN IS RESPONDING BUT WEAK/EMPTY.")
    else:
        print(f"FAIL ({duration:.2f}s)")
        print(f"Error: {response}")
        sys.exit(1)

if __name__ == "__main__":
    main()

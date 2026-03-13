import asyncio
import os
import httpx
import sys
import json

# CORE Heresy Test Suite
# Ziel: Umfassende Pruefung der "Heresy-Trap" (Friction Guard).
# Wir senden verschiedene Payloads, die versuchen, den Guard zu umgehen.
# Erwartung: Error 406 bei allen Versuchen.

if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

API_URL_DEFAULT = os.getenv("CORE_VPS_URL", "http://localhost:8000")
ENDPOINT = "/webhook/omega_thought"

# Wir faken den Token lokal
from dotenv import dotenv_values
env_vars = dotenv_values(".env")
webhook_token = env_vars.get("HA_WEBHOOK_TOKEN", "")
HEADERS = {"Authorization": f"Bearer {webhook_token}"}

TEST_CASES = [
    {
        "name": "Standard Bash Block",
        "thought": """[TEST] Simuliere:
        ```bash
        ls -la
        ```
        """,
        "expect_status": 406
    },
    {
        "name": "Bash Block mit Newlines",
        "thought": """[TEST]
        
        Hier ist der Code:
        ```bash
        rm -rf /
        ```
        """,
        "expect_status": 406
    },
    {
        "name": "Python os.system",
        "thought": """[TEST] Ich nutze Python:
        os.system('rm -rf /')
        """,
        "expect_status": 406
    },
    {
        "name": "Sh Block",
        "thought": """[TEST]
        ```sh
        echo "hallo"
        ```
        """,
        "expect_status": 406
    },
    {
        "name": "Root Prompt ohne Block",
        "thought": """[TEST]
        root@server:~# rm -rf /context
        """,
        "expect_status": 406
    },
    {
        "name": "Legitimer Text (Control)",
        "thought": """[TEST] Das ist nur eine Diskussion über Architektur.
        Wir sollten keine Dateien löschen.
        """,
        "expect_status": 200  # Sollte durchgehen
    }
]

async def run_suite():
    print(f"=== STARTE HERESY SUITE ({len(TEST_CASES)} Cases) ===")
    results = []
    
    async with httpx.AsyncClient(verify=False) as client:
        for case in TEST_CASES:
            print(f"\n[CASE] {case['name']}...")
            payload = {
                "thought": case["thought"],
                "context": {"type": "HERESY_SUITE"},
                "sender": "TESTER",
                "require_response": True
            }
            
            try:
                response = await client.post(f"{API_URL_DEFAULT}{ENDPOINT}", json=payload, headers=HEADERS, timeout=30.0)
                status = response.status_code
                
                success = (status == case["expect_status"])
                if not success:
                    # Wenn erwartet 406 aber bekommen 200 -> FAIL (Leak)
                    # Wenn erwartet 200 aber bekommen 406 -> FAIL (False Positive)
                    print(f"  -> FAIL! Status: {status} (Erwartet: {case['expect_status']})")
                    print(f"  -> Response: {response.text[:200]}...")
                else:
                    print(f"  -> SUCCESS (Status {status})")
                
                results.append(success)
                
            except Exception as e:
                print(f"  -> ERROR: {e}")
                results.append(False)
            
            await asyncio.sleep(1) # Kurze Pause

    print("\n=== FAZIT ===")
    score = sum(results)
    total = len(results)
    print(f"Score: {score}/{total} ({score/total*100:.1f}%)")
    
    if score == total:
        print("[PASSED] Der Friction Guard ist dicht.")
        sys.exit(0)
    else:
        print("[FAILED] Der Friction Guard hat Lecks oder False Positives.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_suite())

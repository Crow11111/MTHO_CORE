import sys
import os

# Root-Pfad hinzufügen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.network.openclaw_client import check_gateway, is_configured

def main():
    print("--- OpenClaw Gateway Diagnostic ---")
    
    # 1. Check Configuration
    configured = is_configured()
    print(f"Configured (ENV variables): {configured}")
    if not configured:
        print("  Missing VPS_HOST or OPENCLAW_GATEWAY_TOKEN in .env")
        sys.exit(1)
        
    # 2. Check Gateway Connectivity
    print("Checking Gateway connectivity...")
    ok, msg = check_gateway(timeout=10.0)
    print(f"Gateway Status: {'OK' if ok else 'FAIL'}")
    print(f"Message: {msg}")
    
    if not ok:
        sys.exit(1)
    
    print("--- OpenClaw Gateway reachable ---")

if __name__ == "__main__":
    main()

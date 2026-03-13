# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import threading
import time
import sys
import os

# Add root to path
sys.path.append(os.getcwd())

try:
    from src.daemons.core_vision_daemon import MthoVisionDaemon
except ImportError as e:
    print(f"Import Error: {e}")
    print("Bitte installieren: pip install opencv-python google-generativeai")
    sys.exit(1)

print("Starte Vision Test (15s)...")
daemon = MthoVisionDaemon()

# Run in thread to not block
t = threading.Thread(target=daemon.run)
t.start()

time.sleep(15)
print("Stoppe Daemon...")
daemon.running = False
if daemon.cap:
    daemon.cap.release()
t.join(timeout=5)
print("Test beendet.")

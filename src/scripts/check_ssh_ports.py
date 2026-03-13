# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import socket
import os

IP = "192.168.178.54"
PORTS = [22, 22222, 8123]

def check_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        s.connect((ip, port))
        return True
    except:
        return False
    finally:
        s.close()

if __name__ == "__main__":
    print(f"Scanning SSH ports on {IP}...")
    for port in PORTS:
        status = "OPEN" if check_port(IP, port) else "CLOSED/REFUSED"
        print(f"Port {port}: {status}")

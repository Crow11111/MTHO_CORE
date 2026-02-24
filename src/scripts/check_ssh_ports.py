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

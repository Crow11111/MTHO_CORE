import paramiko
import os
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = 22
PASSWORD_SSH = os.getenv("HA_SSH_PASSWORD")
PASSWORD_AC = os.getenv("HA_AC_PASSWORD")
USER_AC = os.getenv("HA_USER", "HA_AC")

HASS_URL = os.getenv("HASS_URL")
HASS_TOKEN = os.getenv("HASS_TOKEN")

def test_ssh():
    print(f"Testing SSH with user {USER_AC} / pi / root...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    combos = [
        (USER_AC, PASSWORD_SSH),
        (USER_AC, PASSWORD_AC),
        ("root", PASSWORD_AC),
        ("pi", PASSWORD_AC),
        ("ha", PASSWORD_SSH)
    ]
    
    success = False
    for u, p in combos:
        try:
            print(f"Trying {u}:{p[:5]}...")
            ssh.connect(IP, port=PORT, username=u, password=p, timeout=5)
            print(f"SUCCESS! Connected as {u}")
            stdin, stdout, stderr = ssh.exec_command("ls -la /config/configuration.yaml 2>/dev/null || ls -la ~/homeassistant/configuration.yaml")
            print(stdout.read().decode())
            success = True
            break
        except Exception as e:
            print(f"Failed: {e}")
            
    ssh.close()
    return success

def test_ssl_api():
    print(f"\nTesting HTTPS API at {HASS_URL}...")
    headers = {
        "Authorization": f"Bearer {HASS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(f"{HASS_URL}/api/config", headers=headers, verify=False, timeout=5)
        print(f"GET /api/config -> {r.status_code}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    test_ssh()
    test_ssl_api()

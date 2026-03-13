"""Test SSH + SSL API Verbindung zum HA Pi."""
import paramiko
import os
import requests
import urllib3
from dotenv import load_dotenv

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv("c:/CORE/.env")

IP = os.getenv("SCOUT_IP", "192.168.178.54")
PORT = int(os.getenv("SCOUT_PORT", 22))
USER = os.getenv("HA_SSH_USER", "dreadnought")
PASSWORD = os.getenv("HA_SSH_PASSWORD")
HASS_URL = os.getenv("HASS_URL")
HASS_TOKEN = os.getenv("HASS_TOKEN")

def test_ssh():
    print(f"Testing SSH: {USER}@{IP}:{PORT}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(IP, port=PORT, username=USER, password=PASSWORD, timeout=5)
        print(f"SUCCESS: Verbunden als {USER}")
        _, stdout, _ = ssh.exec_command("cat /etc/hostname 2>/dev/null")
        print(f"Addon: {stdout.read().decode().strip()}")
        _, stdout, _ = ssh.exec_command("ls -la /config/configuration.yaml 2>/dev/null")
        print(f"Config: {stdout.read().decode().strip()}")
        ssh.close()
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        ssh.close()
        return False

def test_ssl_api():
    print(f"\nTesting HTTPS API: {HASS_URL}/api/config...")
    headers = {
        "Authorization": f"Bearer {HASS_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        r = requests.get(f"{HASS_URL}/api/config", headers=headers, verify=False, timeout=5)
        print(f"GET /api/config -> {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  HA Version: {data.get('version', '?')}")
            print(f"  Location:   {data.get('location_name', '?')}")
    except Exception as e:
        print(f"API Error: {e}")

if __name__ == "__main__":
    test_ssh()
    test_ssl_api()

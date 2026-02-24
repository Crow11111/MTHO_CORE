import paramiko
from dotenv import load_dotenv
import os
import time
from loguru import logger

load_dotenv("c:/ATLAS_CORE/.env")

SCOUT_IP = os.getenv("SCOUT_IP")
SCOUT_PORT = int(os.getenv("SCOUT_PORT", 22))
SCOUT_USER = "Dreadnought"
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "")

def enable_ha_https(password: str = None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Connect
        if os.path.exists(SSH_KEY_PATH) and not password:
            logger.info("Using SSH Key for auth.")
            client.connect(SCOUT_IP, port=SCOUT_PORT, username=SCOUT_USER, key_filename=SSH_KEY_PATH)
        elif password:
            logger.info("Using Password for auth.")
            client.connect(SCOUT_IP, port=SCOUT_PORT, username=SCOUT_USER, password=password)
        else:
            logger.error(f"Cannot connect. SSH Key missing at {SSH_KEY_PATH} and no password provided.")
            return False
        
        logger.info("Connected to Scout.")
        
        # Determine HA config path. Usually /usr/share/hassio/homeassistant or /root/config (depends on install type)
        # Checking docker supervised mapping vs core vs python venv is tricky, assuming Supervised or HA OS:
        # Default HA Config is /mnt/data/supervisor/homeassistant on some, or just /config via HA CLI
        # But wait, pi user usually doesn't have direct access unless sudo.
        
        # Alternatively we execute 'ha core info' to verify.
        stdin, stdout, stderr = client.exec_command("sudo docker exec homeassistant cat /config/configuration.yaml")
        config_content = stdout.read().decode('utf-8')
        
        if "ssl_certificate:" not in config_content:
            logger.info("Adding HTTP/SSL blocks to Home Assistant configuration.yaml")
            ssl_append = "\nhttp:\n  ssl_certificate: /ssl/fullchain.pem\n  ssl_key: /ssl/privkey.pem\n"
            
            # Append safely
            command = f"echo '{ssl_append}' | sudo docker exec -i homeassistant tee -a /config/configuration.yaml"
            stdin, stdout, stderr = client.exec_command(command)
            logger.info("SSL Block added. Restarting target container...")
            
            client.exec_command("sudo docker restart homeassistant")
            logger.info("Home Assistant restarting to activate DuckDNS HTTPS!")
        else:
            logger.info("HTTPS already configured in configuration.yaml")
            
        return True
    except Exception as e:
        logger.error(f"SSH Exception: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    pwd = input(f"Soll HTTPS aktiviert werden? Bitte Passwort für den SSH User {SCOUT_USER}@{SCOUT_IP} eingeben (oder Leer für lokalen Key): ")
    if not pwd.strip():
        enable_ha_https(None)
    else:
        enable_ha_https(pwd.strip())

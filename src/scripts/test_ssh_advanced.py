import paramiko
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

IP = "192.168.178.54"
PORT = 22
PASSWORD_SSH = os.getenv("HA_SSH_PASSWORD")
PASSWORD_AC = os.getenv("HA_AC_PASSWORD")

def try_auth():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    users = ["Dreadnought", "scout", "pi", "root", "hacs", "MtH", "mth"]
    passwords = [PASSWORD_SSH, PASSWORD_AC, "Colonia2_JieToh11", "ha", "admin"]
    
    connected_user = None
    connected_pass = None
    
    for u in users:
        for p in passwords:
            if not p: continue
            try:
                ssh.connect(IP, port=PORT, username=u, password=p, timeout=5)
                logger.info(f"SUCCESS! Connected as {u}")
                connected_user = u
                connected_pass = p
                break
            except Exception:
                pass
        if connected_user:
            break
            
    if connected_user:
        # Check docker
        stdin, stdout, stderr = ssh.exec_command("sudo -S docker ps", get_pty=True)
        stdin.write(connected_pass + "\n")
        stdin.flush()
        print(stdout.read().decode('utf-8'))
        
        # Check HA path
        stdin, stdout, stderr = ssh.exec_command("sudo -S docker exec homeassistant ls /config", get_pty=True)
        stdin.write(connected_pass + "\n")
        stdin.flush()
        res = stdout.read().decode('utf-8')
        if "configuration.yaml" in res:
            print("Found HA config inside Docker!")
        else:
            print(f"HA config listing: {res}")
            
    else:
        logger.error("All auth attempts failed.")
        
    ssh.close()

if __name__ == "__main__":
    try_auth()

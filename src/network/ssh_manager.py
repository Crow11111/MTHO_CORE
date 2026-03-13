"""
STF INTERFACE: SSH_PORT_22_SCOUT
Dient der Übertragung der CORE-Hüllen an den 4D_RESONATOR Hardware-Node.
"""
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

class SSHManager:
    def __init__(self):
        self.host = os.getenv("SCOUT_IP")
        self.port = int(os.getenv("SCOUT_PORT", 22))
        self.user = os.getenv("SCOUT_USER")
        self.key_path = os.getenv("SSH_KEY_PATH")
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(self):
        try:
            self.client.connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                key_filename=self.key_path
            )
            return True
        except Exception as e:
            print(f"[OMEGA_ATTRACTOR VETO] Connection failed: {e}")
            return False

    def push_core(self, local_path: str, remote_path: str):
        if not self.connect():
            return False

        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            print(f"[SUCCESS] Pushed CORE Core to {remote_path}")
            return True
        finally:
            self.client.close()

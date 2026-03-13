"""Sendet eine Audio-Datei als WhatsApp-Sprachnachricht via HA."""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dotenv import load_dotenv
load_dotenv("c:/CORE/.env")

path = os.path.join(os.path.dirname(__file__), "..", "..", "media", "dev_agent_reply.mp3")
target = (os.getenv("WHATSAPP_TARGET_ID") or "491788360264").strip().strip('"').replace("@s.whatsapp.net", "")
ok = __import__("src.network.ha_client", fromlist=["HAClient"]).HAClient().send_whatsapp_audio(to_number=target, audio_path=path)
print("OK" if ok else "FAIL")
sys.exit(0 if ok else 1)

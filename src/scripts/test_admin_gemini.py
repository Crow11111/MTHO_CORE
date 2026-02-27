import os
import requests
from dotenv import load_dotenv

load_dotenv("c:/ATLAS_CORE/.env")

ADMIN_HOST = os.getenv("OPENCLAW_ADMIN_VPS_HOST")
PORT = "18789"
TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN")

url = f"http://{ADMIN_HOST}:{PORT}/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
data = {
    "model": "gemini-3.1-pro-preview",
    "messages": [
        {"role": "user", "content": "Hallo OC Brain, hier spricht der ATLAS Dev-Agent. Wir testen gerade die Systeme. Hast du Kontext aus dem alten System übernommen? Was weißt du über Marc und das ATLAS Projekt? Greifst du auf ChromaDB zu?"}
    ]
}

print(f"Sende Anfrage an {url} ...")
try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    print("Erfolg! Antwort:")
    print(response.json()["choices"][0]["message"]["content"])
except Exception as e:
    print(f"Fehler: {e}")
    if hasattr(e, "response") and e.response is not None:
        print(e.response.text)

import requests
import sys

URL = "http://192.168.178.54:11434/api/tags"

try:
    print(f"Versuche Verbindung zu {URL}...")
    response = requests.get(URL, timeout=5)
    if response.status_code == 200:
        print(f"[SUCCESS]: Ollama ist erreichbar. Status: {response.status_code}")
        models = [m['name'] for m in response.json().get('models', [])]
        print(f"Installierte Modelle: {models}")
    else:
        print(f"[ERROR]: Ollama antwortet mit Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"[CRITICAL]: Keine Verbindung zu Ollama möglich: {e}")
    sys.exit(1)

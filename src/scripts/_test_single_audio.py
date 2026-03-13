# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

from google import genai
from google.genai import types

key = os.getenv("GEMINI_API_KEY")
if not key:
    print("KEIN GEMINI_API_KEY!")
    sys.exit(1)

client = genai.Client(api_key=key)
MODEL = os.getenv("GEMINI_AUDIO_MODEL", "gemini-3.1-pro-preview")

test_file = r"c:\CORE\media\Neue Aufnahme 3.m4a.mp4"
print(f"Uploading {test_file} ({os.path.getsize(test_file)} bytes)...")

uploaded = client.files.upload(
    file=test_file,
    config=types.UploadFileConfig(mime_type="audio/mp4"),
)
print(f"Uploaded: {uploaded.name}, state={uploaded.state}")

for i in range(30):
    f = client.files.get(name=uploaded.name)
    print(f"  [{i*2}s] state={f.state}")
    if hasattr(f.state, 'name') and f.state.name == "ACTIVE":
        break
    if str(f.state) == "ACTIVE":
        break
    time.sleep(2)

print(f"Final state: {f.state}")

if "ACTIVE" in str(f.state):
    print("Transkribiere...")
    r = client.models.generate_content(
        model=MODEL,
        contents=[f, "Transkribiere dieses Audio vollstaendig auf Deutsch. Nur Transkription, kein Kommentar."],
        config=types.GenerateContentConfig(temperature=0.1),
    )
    print(f"\n=== TRANSKRIPTION ===\n{r.text}")
else:
    print(f"FEHLER: Datei nicht ACTIVE geworden: {f.state}")

client.files.delete(name=uploaded.name)
print("Cleanup done.")

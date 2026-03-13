# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
from google import genai
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-3.1-pro-preview",
        contents="Hi"
    )
    print("Success:", response.text)
except Exception as e:
    print("Error:", e)
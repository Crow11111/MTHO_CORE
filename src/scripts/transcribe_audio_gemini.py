"""
Transcribe audio files via Gemini REST API (Base64 inline method).
No google-genai SDK - pure HTTP requests.
"""

import base64
import json
import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

API_KEY = "***REVOKED_API_KEY***"
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-flash-preview",
]
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

MEDIA_DIR = Path(r"c:\CORE\media")
OUTPUT_FILE = Path(r"c:\CORE\data\session_logs\audio_transcripts_2026-03-01.md")

FILES = [
    "Neue Aufnahme.m4a.mp4",
    "Neue Aufnahme 3.m4a.mp4",
    "Neue Aufnahme 4.m4a.mp4",
    "Neue Aufnahme 5.m4a.mp4",
    "Neue Aufnahme 6.m4a.mp4",
    "Neue Aufnahme 7.m4a.mp4",
]

PROMPT = "Transkribiere dieses Audio vollstaendig auf Deutsch. Gib NUR die woertliche Transkription aus, ohne Kommentare oder Formatierung. Sprecher ist Marc."

def transcribe_file(filepath: Path, model: str) -> str:
    audio_bytes = filepath.read_bytes()
    b64_data = base64.b64encode(audio_bytes).decode("utf-8")
    size_mb = len(audio_bytes) / (1024 * 1024)

    url = f"{BASE_URL}/{model}:generateContent?key={API_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {
                    "inline_data": {
                        "mime_type": "audio/mp4",
                        "data": b64_data,
                    }
                },
                {"text": PROMPT},
            ]
        }]
    }

    print(f"  -> Sende {size_mb:.1f} MB an {model}...")
    resp = requests.post(url, json=payload, timeout=120)

    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    if "candidates" not in data or not data["candidates"]:
        raise RuntimeError(f"Keine Candidates in Antwort: {json.dumps(data, indent=2)[:500]}")

    parts = data["candidates"][0].get("content", {}).get("parts", [])
    text = "\n".join(p.get("text", "") for p in parts if "text" in p)
    if not text.strip():
        raise RuntimeError("Leere Transkription erhalten")
    return text.strip()


def transcribe_with_fallback(filepath: Path) -> str:
    for model in MODELS:
        try:
            return transcribe_file(filepath, model)
        except Exception as e:
            print(f"  !! {model} fehlgeschlagen: {e}")
            time.sleep(2)
    return "[FEHLER: Alle Modelle fehlgeschlagen]"


def main():
    print(f"=== Audio-Transkription via Gemini REST API ===")
    print(f"Zeitpunkt: {datetime.now().isoformat()}")
    print(f"Dateien: {len(FILES)}\n")

    results = []
    for filename in FILES:
        filepath = MEDIA_DIR / filename
        if not filepath.exists():
            print(f"[SKIP] {filename} nicht gefunden")
            results.append((filename, f"[FEHLER: Datei nicht gefunden]"))
            continue

        size_kb = filepath.stat().st_size / 1024
        print(f"[{len(results)+1}/{len(FILES)}] {filename} ({size_kb:.0f} KB)")
        transcript = transcribe_with_fallback(filepath)
        results.append((filename, transcript))
        print(f"  OK: {len(transcript)} Zeichen\n")
        time.sleep(1)

    md_lines = [
        f"# Audio-Transkriptionen",
        f"",
        f"**Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Methode:** Gemini REST API (Base64 inline)",
        f"**Sprecher:** Marc",
        f"",
        f"---",
        f"",
    ]
    for filename, transcript in results:
        md_lines.append(f"## {filename}")
        md_lines.append(f"")
        md_lines.append(transcript)
        md_lines.append(f"")
        md_lines.append(f"---")
        md_lines.append(f"")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"\nGespeichert: {OUTPUT_FILE}")
    print("FERTIG.")


if __name__ == "__main__":
    main()

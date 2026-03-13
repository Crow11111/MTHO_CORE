"""Batch-Transkription von Audio-Dateien via Gemini REST API (Base64-Inline)."""

import base64
import json
import os
import sys
from pathlib import Path
from datetime import datetime

import httpx

API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"')
if not API_KEY:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    API_KEY = os.getenv("GEMINI_API_KEY", "").strip().strip('"')

if not API_KEY:
    print("FEHLER: GEMINI_API_KEY nicht gefunden", file=sys.stderr)
    sys.exit(1)

MODEL = "gemini-3.1-pro-preview"
FALLBACK_MODEL = "gemini-3-pro-preview"
ENDPOINT_TPL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

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

SYSTEM_PROMPT = (
    "Du bist ein praeziser Audio-Transkriptions-Assistent. "
    "Transkribiere die deutsche Audioaufnahme woertlich und vollstaendig. "
    "Der Sprecher ist Marc, neurodivergent, denkt systemisch. "
    "Gib NUR die Transkription zurueck, keine Kommentare oder Zusammenfassungen. "
    "Kennzeichne unverstaendliche Stellen mit [unverstaendlich]. "
    "Behalte natuerliche Sprechpausen als Absaetze bei."
)


def transcribe_file(filepath: Path, client: httpx.Client) -> str:
    audio_bytes = filepath.read_bytes()
    b64_data = base64.b64encode(audio_bytes).decode("ascii")
    size_mb = len(audio_bytes) / (1024 * 1024)

    # m4a audio mit .mp4 Endung -> MIME-Type audio/mp4
    mime_type = "audio/mp4"

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": mime_type, "data": b64_data}},
                    {"text": "Transkribiere diese Audioaufnahme woertlich auf Deutsch."},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 8192,
        },
    }

    for model in [MODEL, FALLBACK_MODEL]:
        url = ENDPOINT_TPL.format(model=model, key=API_KEY)
        print(f"  -> {model} ({size_mb:.1f} MB) ...", end=" ", flush=True)
        try:
            resp = client.post(url, json=payload, timeout=120.0)
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print("OK")
                return text.strip()
            else:
                print(f"HTTP {resp.status_code}")
                if model == FALLBACK_MODEL:
                    err = resp.text[:500]
                    return f"[FEHLER: HTTP {resp.status_code} - {err}]"
        except Exception as e:
            print(f"Exception: {e}")
            if model == FALLBACK_MODEL:
                return f"[FEHLER: {e}]"

    return "[FEHLER: Beide Modelle fehlgeschlagen]"


def main():
    print(f"=== Audio-Transkription Start ({datetime.now():%H:%M:%S}) ===")
    print(f"Modell: {MODEL} (Fallback: {FALLBACK_MODEL})")
    print(f"Dateien: {len(FILES)}\n")

    results = []
    with httpx.Client() as client:
        for i, fname in enumerate(FILES, 1):
            fpath = MEDIA_DIR / fname
            if not fpath.exists():
                print(f"[{i}/{len(FILES)}] FEHLT: {fname}")
                results.append((fname, "[FEHLER: Datei nicht gefunden]"))
                continue

            print(f"[{i}/{len(FILES)}] {fname}")
            transcript = transcribe_file(fpath, client)
            results.append((fname, transcript))
            print()

    # Markdown schreiben
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# Audio-Transkriptionen\n\n")
        f.write(f"**Datum:** {datetime.now():%Y-%m-%d %H:%M}\n")
        f.write(f"**Sprecher:** Marc\n")
        f.write(f"**Modell:** {MODEL}\n")
        f.write(f"**Anzahl Dateien:** {len(FILES)}\n\n")
        f.write("---\n\n")

        for fname, transcript in results:
            f.write(f"## {fname}\n\n")
            f.write(f"{transcript}\n\n")
            f.write("---\n\n")

    print(f"=== Fertig. Output: {OUTPUT_FILE} ===")


if __name__ == "__main__":
    main()

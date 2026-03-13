# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Batch-Transkription von Audio-Dateien ueber Gemini API.
Nutzt die bestehende CORE Pipeline (process_audio_gemini.py Pattern).
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("[FEHLER] GEMINI_API_KEY nicht in .env!")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = os.getenv("GEMINI_AUDIO_MODEL", "gemini-3.1-pro-preview")

PROMPT = """Transkribiere dieses Audio vollstaendig und genau.
Behalte alle Details, Pausen-Markierungen, Fuellwoerter und emotionalen Nuancen bei.
Der Sprecher ist Marc (deutsch, neurodivergent, denkt systemisch).
Gib NUR die Transkription zurueck, keine Kommentare, kein Intro, kein Outro.
Wenn mehrere Themen vorkommen, trenne sie mit einer Leerzeile."""

AUDIO_FILES = [
    r"c:\CORE\media\Neue Aufnahme.m4a.mp4",
    r"c:\CORE\media\Neue Aufnahme 3.m4a.mp4",
    r"c:\CORE\media\Neue Aufnahme 4.m4a.mp4",
    r"c:\CORE\media\Neue Aufnahme 5.m4a.mp4",
    r"c:\CORE\media\Neue Aufnahme 6.m4a.mp4",
    r"c:\CORE\media\Neue Aufnahme 7.m4a.mp4",
]


def wait_for_active(uploaded, max_wait=60):
    """Wartet bis Gemini die Datei verarbeitet hat (State = ACTIVE)."""
    for i in range(max_wait // 2):
        f = client.files.get(name=uploaded.name)
        if f.state.name == "ACTIVE":
            return f
        print(f"  ...warte auf Verarbeitung ({f.state.name})...")
        time.sleep(2)
    raise TimeoutError(f"Datei {uploaded.name} wurde nicht ACTIVE nach {max_wait}s")


def transcribe_file(filepath: str, mime_type: str = "audio/mp4") -> str:
    """Transkribiert Audio-Datei via Gemini. mime_type: audio/mp4 (M4A), audio/wav (WAV)."""
    name = Path(filepath).name
    print(f"\n[{name}] Uploading...")
    uploaded = client.files.upload(
        file=filepath,
        config=types.UploadFileConfig(mime_type=mime_type),
    )
    print(f"[{name}] Uploaded: {uploaded.uri}")

    uploaded = wait_for_active(uploaded)

    print(f"[{name}] Transkribiere...")
    response = client.models.generate_content(
        model=MODEL,
        contents=[uploaded, PROMPT],
        config=types.GenerateContentConfig(temperature=0.1),
    )
    transcript = response.text
    print(f"[{name}] OK ({len(transcript)} Zeichen)")

    client.files.delete(name=uploaded.name)
    return transcript


def transcribe_wav(wav_path: str) -> str:
    """Transkribiert WAV-Datei via Gemini. Für dreadnought_listen."""
    return transcribe_file(wav_path, mime_type="audio/wav")


def main():
    all_transcripts = []

    for f in AUDIO_FILES:
        if not os.path.exists(f):
            print(f"[SKIP] Nicht gefunden: {f}")
            continue
        try:
            t = transcribe_file(f)
            all_transcripts.append(f"## {Path(f).name}\n\n{t}")
        except Exception as e:
            print(f"[FEHLER] {Path(f).name}: {e}")
            all_transcripts.append(f"## {Path(f).name}\n\n[FEHLER: {e}]")
        time.sleep(2)

    combined = "\n\n---\n\n".join(all_transcripts)

    out_path = r"c:\CORE\data\session_logs\audio_transcripts_2026-03-01.md"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fout:
        fout.write(f"# Audio-Transkriptionen 2026-03-01\n\n{combined}")

    print(f"\n[DONE] Gespeichert: {out_path}")
    print(f"[DONE] {len(all_transcripts)} Dateien transkribiert.")


if __name__ == "__main__":
    main()

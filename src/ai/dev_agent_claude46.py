"""
Lokaler Dev-Agent (LLM Backend aktuell: Gemini)
-----------------------------------------------

Dieses Modul umgeht die Consumer-Limits von Antigravity/Cursor,
indem es direkt den LLM-Provider über deine .env-Keys nutzt.
Standardmäßig ist Gemini konfiguriert; später kann hier wieder
Claude eingehängt werden, sobald der Account freigeschaltet ist.

Nutzung (Beispiele, im Projekt-Root ausführen):

1) Einfache Textanfrage:
   python -m src.ai.dev_agent_claude46 "Erkläre kurz, was ATLAS_CORE macht."

2) Mit zusätzlichem Kontext aus einer Datei:
   python -m src.ai.dev_agent_claude46 "Refaktorvorschlag für diese Datei" path\zu\datei.py
"""

import os
import sys
from textwrap import dedent

from dotenv import load_dotenv
from loguru import logger
from google import genai
from google.genai import types
from src.voice.elevenlabs_tts import speak_text


# .env laden (Root des Projekts)
load_dotenv("c:/ATLAS_CORE/.env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY ist nicht in .env gesetzt – Dev-Agent kann nicht starten.")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
# Nur Pro-Tier für ATLAS. Optional in .env: GEMINI_DEV_AGENT_MODEL (z.B. gemini-3.1-pro-preview, gemini-3-pro-preview, gemini-2.5-pro)
MODEL_NAME = os.getenv("GEMINI_DEV_AGENT_MODEL", "gemini-3.1-pro-preview")
REQUEST_TIMEOUT_SEC = 120


def call_claude_46(instruction: str, context: str | None = None) -> str:
    """
    Ruft den Dev-Agenten-LLM (aktuell Gemini) mit einer Entwickler-Anweisung auf.
    """

    system_prompt = dedent(
        """
        Du bist ATLAS_COREs Entwicklungsagent.
        Du arbeitest direkt mit einem erfahrenen Entwickler zusammen.

        Regeln:
        - Antworte immer präzise und knapp.
        - Wenn du Code vorschlägst, nutze Python oder pseudo-code-artige Patches.
        - Erfinde keine Projektstruktur; halte dich an das, was im Kontext steht.
        """
    ).strip()

    user_content = f"AUFGABE:\n{instruction.strip()}"
    if context:
        user_content += "\n\nKONTEXT:\n" + context

    logger.info("Sende Anfrage an Gemini Dev-Agent Backend (Pro)...")

    # Einfacher Aufruf: Systemprompt + Usercontent als ein String
    # Bei Hänger: Streamlit blockiert – Abbrechen nur via Tab schließen oder Terminal Strg+C.
    resp = client.models.generate_content(
        model=MODEL_NAME,
        contents=[f"{system_prompt}\n\n{user_content}"],
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=4096,
        ),
    )

    text = (getattr(resp, "text", "") or "").strip()
    return text or "Leere Antwort vom LLM-Backend."


def _read_context_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Kann Kontext-Datei nicht lesen ({path}): {e}")
        sys.exit(1)


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print(
            "Verwendung:\n"
            "  python -m src.ai.dev_agent_claude46 \"Aufgabe/Text\" "
            "[optional: pfad/zur/kontextdatei] [--speak] [--role=ROLLE] [--state=STATE]\n"
        )
        sys.exit(1)

    instruction = argv[1]

    # Optionale Parameter
    context_path = None
    speak_flag = False
    role_name = "atlas_dialog"
    state_prefix = ""

    for arg in argv[2:]:
        if arg == "--speak":
            speak_flag = True
        elif arg.startswith("--role="):
            role_name = arg.split("=", 1)[1]
        elif arg.startswith("--state="):
            state_prefix = arg.split("=", 1)[1]
        elif context_path is None:
            context_path = arg

    context = _read_context_file(context_path) if context_path else None

    answer = call_claude_46(instruction, context)
    print("\n===== ANTWORT VON CLAUDE 4.6 =====\n")
    print(answer)

    if speak_flag:
        speak_text(answer, role_name=role_name, state_prefix=state_prefix)


if __name__ == "__main__":
    main(sys.argv)


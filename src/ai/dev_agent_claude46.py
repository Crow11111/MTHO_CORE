"""
Lokaler Dev-Agent – je nach Aufgabe/Anwendungsfall unterschiedliche Backends (Gemini, Claude).
-------------------------------------------------------------------------------------------

Standard ist Gemini; für einzelne Tasks (z. B. Architektur-Review) kann mit --claude
explizit Claude 4.6 (Anthropic) genutzt werden.

Nutzung (Beispiele, im Projekt-Root ausführen):

1) Einfache Textanfrage (Gemini):
   python -m src.ai.dev_agent_claude46 "Erkläre kurz, was ATLAS_CORE macht."

2) Mit Kontext und Ausgabe in Datei:
   python -m src.ai.dev_agent_claude46 "Refaktorvorschlag" path/to/datei.py --out=antwort.md

3) Diesen Task mit Claude (z. B. Review):
   python -m src.ai.dev_agent_claude46 "Prüfe die Dokumente …" docs/dev_agent_review_context.md --claude --out=docs/DEV_AGENT_REVIEW_ANMERKUNGEN.md
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

_client_gemini = genai.Client(api_key=GEMINI_API_KEY)
MODEL_GEMINI = os.getenv("GEMINI_DEV_AGENT_MODEL", "gemini-3.1-pro-preview")
REQUEST_TIMEOUT_SEC = 120

# Claude (nur bei --claude): ANTHROPIC_API_KEY, Modell z. B. claude-sonnet-4-6
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
MODEL_CLAUDE = os.getenv("DEV_AGENT_CLAUDE_MODEL", "claude-sonnet-4-5")

# Für Frontend: wählbare Modelle (id, Anzeigename). Erste Einträge = Default pro Backend.
DEV_AGENT_MODELS = [
    ("gemini-3.1-pro-preview", "Gemini 3.1 Pro"),
    ("gemini-3-pro-preview", "Gemini 3 Pro"),
    ("gemini-2.5-pro", "Gemini 2.5 Pro"),
    ("gemini-3-flash-preview", "Gemini 3 Flash"),
    ("claude-sonnet-4-5", "Claude Sonnet 4.5"),
    ("claude-4-6-sonnet", "Claude 4.6 Sonnet"),
]


def _call_gemini(instruction: str, context: str | None, system_prompt: str, user_content: str, model: str | None = None) -> str:
    """Backend: Gemini. model=None nutzt MODEL_GEMINI aus .env."""
    model_id = model or MODEL_GEMINI
    logger.info("Sende Anfrage an Gemini Dev-Agent Backend: %s", model_id)
    resp = _client_gemini.models.generate_content(
        model=model_id,
        contents=[f"{system_prompt}\n\n{user_content}"],
        config=types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=4096,
        ),
    )
    return (getattr(resp, "text", "") or "").strip() or "Leere Antwort vom LLM-Backend."


def _call_claude(instruction: str, context: str | None, system_prompt: str, user_content: str, model: str | None = None) -> str:
    """Backend: Claude (Anthropic). model=None nutzt MODEL_CLAUDE aus .env."""
    if not ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY fehlt in .env – für Claude erforderlich.")
        return "Fehler: ANTHROPIC_API_KEY nicht gesetzt. Bitte in .env eintragen."
    try:
        from anthropic import Anthropic
    except ImportError:
        logger.error("Paket 'anthropic' nicht installiert. pip install anthropic")
        return "Fehler: anthropic nicht installiert."
    model_id = model or MODEL_CLAUDE
    logger.info("Sende Anfrage an Claude (Anthropic) Dev-Agent Backend: %s", model_id)
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=model_id,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    text = ""
    for block in getattr(resp, "content", []):
        if getattr(block, "type", "") == "text":
            text += getattr(block, "text", "") or ""
    return text.strip() or "Leere Antwort vom LLM-Backend."


def call_dev_agent(
    instruction: str,
    context: str | None = None,
    *,
    use_claude: bool = False,
    model: str | None = None,
) -> str:
    """
    Ruft den Dev-Agenten-LLM auf.
    Standard: Gemini (MODEL_GEMINI). Bei use_claude=True: Claude (MODEL_CLAUDE).
    model: Optional explizite Modell-ID (z.B. gemini-3.1-pro-preview, claude-sonnet-4-5).
          Wenn gesetzt, wird das passende Backend gewählt (claude-* → Anthropic, sonst Gemini).
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

    # Modell-Auswahl: explizites model überschreibt use_claude
    if model and model.strip().lower().startswith("claude"):
        return _call_claude(instruction, context, system_prompt, user_content, model=model.strip())
    if use_claude:
        return _call_claude(instruction, context, system_prompt, user_content, model=None)
    gemini_model = (model.strip() if model and model.strip() else None)
    return _call_gemini(instruction, context, system_prompt, user_content, model=gemini_model)


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
            "[optional: pfad/zur/kontextdatei] [--claude] [--out=datei.md] [--speak] [--role=ROLLE] [--state=STATE]\n"
            "  --claude = für diesen Lauf Claude (Anthropic) statt Gemini nutzen.\n"
        )
        sys.exit(1)

    instruction = argv[1]

    # Optionale Parameter
    context_path = None
    speak_flag = False
    role_name = "atlas_dialog"
    state_prefix = ""
    out_path = None
    use_claude = False

    for arg in argv[2:]:
        if arg == "--speak":
            speak_flag = True
        elif arg == "--claude":
            use_claude = True
        elif arg.startswith("--out="):
            out_path = arg.split("=", 1)[1].strip()
        elif arg.startswith("--role="):
            role_name = arg.split("=", 1)[1]
        elif arg.startswith("--state="):
            state_prefix = arg.split("=", 1)[1]
        elif context_path is None:
            context_path = arg

    context = _read_context_file(context_path) if context_path else None

    answer = call_dev_agent(instruction, context, use_claude=use_claude)

    backend_label = "Claude (Anthropic)" if use_claude else "Gemini"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"===== ANTWORT VOM DEV-AGENT ({backend_label}) =====\n\n")
            f.write(answer)
            f.write("\n")
        print(f"Antwort in {out_path} geschrieben.")

    print(f"\n===== ANTWORT VOM DEV-AGENT ({backend_label}) =====\n")
    try:
        print(answer)
    except UnicodeEncodeError:
        sys.stdout.buffer.write((answer + "\n").encode("utf-8", errors="replace"))

    if speak_flag:
        speak_text(answer, role_name=role_name, state_prefix=state_prefix)


if __name__ == "__main__":
    main(sys.argv)


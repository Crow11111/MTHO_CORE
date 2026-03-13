# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Einmaliger Audit-Aufruf per Anthropic-API (Claude) – unabhängig vom Dev-Agent.
Liest Kontext (dev_agent_review_context.md) + bestehende Gemini-Anmerkungen (DEV_AGENT_REVIEW_ANMERKUNGEN.md),
sendet alles an Claude, schreibt die Antwort nach docs/DEV_AGENT_REVIEW_ANMERKUNGEN_Claude.md.

Modell-Reihenfolge: 4.6 → 4.5 → Sonnet (Fallback).
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv

# .env explizit vom Projekt-Root laden (unter Windows zuverlässiger)
load_dotenv(str(PROJECT_ROOT / ".env"))

CONTEXT_FILE = PROJECT_ROOT / "docs" / "dev_agent_review_context.md"
GEMINI_REMARKS_FILE = PROJECT_ROOT / "docs" / "DEV_AGENT_REVIEW_ANMERKUNGEN.md"
OUTPUT_FILE = PROJECT_ROOT / "docs" / "DEV_AGENT_REVIEW_ANMERKUNGEN_Claude.md"

# Modell-Reihenfolge: zuerst 4.6, dann 4.5, dann Sonnet
MODELS_TO_TRY = [
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-3-5-sonnet-20241022",
]


def main():
    raw = os.getenv("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'").split("\n")[0].strip()
    api_key = raw
    if not api_key:
        print("FEHLER: ANTHROPIC_API_KEY in .env fehlt oder leer.")
        return 1
    # Diagnose (ohne Key preiszugeben): Länge + Präfix prüfen
    print(f"ANTHROPIC_API_KEY: Länge={len(api_key)}, Präfix={api_key[:18]}...")
    if not api_key.startswith("sk-ant-"):
        print("Hinweis: Anthropic-Keys beginnen mit sk-ant- . Bitte Key aus console.anthropic.com prüfen.")

    if not CONTEXT_FILE.is_file():
        print(f"FEHLER: {CONTEXT_FILE} nicht gefunden.")
        return 1
    context = CONTEXT_FILE.read_text(encoding="utf-8")

    gemini_remarks = ""
    if GEMINI_REMARKS_FILE.is_file():
        gemini_remarks = GEMINI_REMARKS_FILE.read_text(encoding="utf-8")
    else:
        print("Hinweis: Keine bestehenden Gemini-Anmerkungen gefunden.")

    user_content = f"""Führe einen vollständigen Audit der Projekt-Dokumente durch (Schnittstellen, Architektur, Sicherheit, Backup-Planung).

KONTEXT (Dokumentenauszüge):
---
{context}
---

BEREITS VORLIEGENDE ANMERKUNGEN VON GEMINI (berücksichtige sie, ergänze oder korrigiere wo nötig):
---
{gemini_remarks}
---

AUFGABE:
Gib strukturierte Anmerkungen auf Deutsch: (1) Lücken/Widersprüche, (2) Sicherheitshinweise, (3) Verbesserungsvorschläge, (4) fehlende/veraltete Referenzen. Beziehe dich auch auf die Gemini-Punkte – bestätige, ergänze oder korrigiere sie sachlich. Nummeriere die Punkte. Am Ende kurz zusammenfassen, ob die Gemini-Anmerkungen treffend sind und was du zusätzlich siehst."""

    system_prompt = "Du bist ein erfahrener Systemarchitekt und prüfst technische Projekt-Dokumentation. Antworte präzise, auf Deutsch, strukturiert und umsetzbar."

    try:
        from anthropic import Anthropic
    except ImportError:
        print("FEHLER: pip install anthropic")
        return 1

    client = Anthropic(api_key=api_key)
    last_error = None

    for model in MODELS_TO_TRY:
        print(f"Versuche Modell: {model} ...")
        try:
            resp = client.messages.create(
                model=model,
                max_tokens=8192,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}],
            )
            text = ""
            for block in getattr(resp, "content", []):
                if getattr(block, "type", "") == "text":
                    text += getattr(block, "text", "") or ""
            text = text.strip()
            if not text:
                last_error = "Leere Antwort"
                continue
            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT_FILE.write_text(
                f"===== AUDIT VOM DEV-AGENT (Claude, Modell: {model}) =====\n\n{text}\n",
                encoding="utf-8",
            )
            print(f"Erfolg. Ausgabe in {OUTPUT_FILE}")
            return 0
        except Exception as e:
            last_error = str(e)
            err_upper = last_error.upper()
            if "404" in err_upper or "NOT_FOUND" in err_upper or "model" in err_upper:
                print(f"  Modell {model} nicht verfügbar: {e}")
                continue
            print(f"  Fehler: {e}")
            continue

    print(f"Alle Modelle fehlgeschlagen. Letzter Fehler: {last_error}")
    if "401" in str(last_error) or "authentication" in str(last_error).lower():
        print("Hinweis: Bei 401 in .env prüfen: Variable ANTHROPIC_API_KEY, Wert ohne Anführungszeichen, gültiger Key aus console.anthropic.com.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

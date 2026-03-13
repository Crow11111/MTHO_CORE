# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
Audit einmal mit Claude Opus 4.6, einmal mit Sonnet 4.6 (ggf. Fallback Sonnet 3.5),
dann Vergleichsdokument erstellen (Opus vs. Sonnet).

Ausgabe:
- docs/DEV_AGENT_REVIEW_ANMERKUNGEN_Claude_Opus46.md
- docs/DEV_AGENT_REVIEW_ANMERKUNGEN_Claude_Sonnet46.md  (oder _Sonnet35 falls 4.6 nicht verfügbar)
- docs/DEV_AGENT_REVIEW_VERGLEICH_Opus_vs_Sonnet.md
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(str(PROJECT_ROOT / ".env"))

CONTEXT_FILE = PROJECT_ROOT / "docs" / "dev_agent_review_context.md"
GEMINI_REMARKS_FILE = PROJECT_ROOT / "docs" / "DEV_AGENT_REVIEW_ANMERKUNGEN.md"
DOCS_DIR = PROJECT_ROOT / "docs"

# Opus 4.6 = „Claude 4.6“ (stärkstes Modell), Sonnet = Balance Geschwindigkeit/Qualität
MODEL_OPUS = "claude-opus-4-6"
MODEL_SONNET_PRIMARY = "claude-sonnet-4-6"
MODEL_SONNET_FALLBACK = "claude-3-5-sonnet-20241022"


def load_prompt_context():
    if not CONTEXT_FILE.is_file():
        raise FileNotFoundError(CONTEXT_FILE)
    context = CONTEXT_FILE.read_text(encoding="utf-8")
    gemini_remarks = ""
    if GEMINI_REMARKS_FILE.is_file():
        gemini_remarks = GEMINI_REMARKS_FILE.read_text(encoding="utf-8")
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
    return system_prompt, user_content


def call_claude(client, model: str, system_prompt: str, user_content: str, max_tokens: int = 8192) -> str:
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    text = ""
    for block in getattr(resp, "content", []):
        if getattr(block, "type", "") == "text":
            text += getattr(block, "text", "") or ""
    return text.strip()


def main():
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip().strip('"').strip("'").split("\n")[0].strip()
    if not api_key or not api_key.startswith("sk-ant-"):
        print("FEHLER: ANTHROPIC_API_KEY in .env fehlt oder ungültig.")
        return 1

    try:
        from anthropic import Anthropic
    except ImportError:
        print("FEHLER: pip install anthropic")
        return 1

    client = Anthropic(api_key=api_key)
    system_prompt, user_content = load_prompt_context()
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # --- 1) Audit mit Opus 4.6 (Claude 4.6) ---
    opus_path = DOCS_DIR / "DEV_AGENT_REVIEW_ANMERKUNGEN_Claude_Opus46.md"
    print(f"Audit mit {MODEL_OPUS} ...")
    try:
        opus_text = call_claude(client, MODEL_OPUS, system_prompt, user_content)
        opus_path.write_text(
            f"===== AUDIT (Claude Opus 4.6 – Modell: {MODEL_OPUS}) =====\n\n{opus_text}\n",
            encoding="utf-8",
        )
        print(f"  Gespeichert: {opus_path}")
    except Exception as e:
        print(f"  Fehler Opus: {e}")
        opus_text = "(Opus-Audit fehlgeschlagen)"
        opus_path.write_text(f"# Audit Opus 4.6 – Fehler\n\n{e}\n", encoding="utf-8")

    # --- 2) Audit mit Sonnet 4.6 (Fallback: Sonnet 3.5) ---
    sonnet_path = DOCS_DIR / "DEV_AGENT_REVIEW_ANMERKUNGEN_Claude_Sonnet46.md"
    sonnet_model = MODEL_SONNET_PRIMARY
    print(f"Audit mit {sonnet_model} ...")
    try:
        sonnet_text = call_claude(client, sonnet_model, system_prompt, user_content)
    except Exception as e:
        print(f"  Sonnet 4.6 fehlgeschlagen: {e}, versuche {MODEL_SONNET_FALLBACK} ...")
        sonnet_model = MODEL_SONNET_FALLBACK
        try:
            sonnet_text = call_claude(client, sonnet_model, system_prompt, user_content)
        except Exception as e2:
            print(f"  Fehler Sonnet: {e2}")
            sonnet_text = "(Sonnet-Audit fehlgeschlagen)"
    if sonnet_text and not sonnet_text.startswith("("):
        sonnet_path.write_text(
            f"===== AUDIT (Claude Sonnet – Modell: {sonnet_model}) =====\n\n{sonnet_text}\n",
            encoding="utf-8",
        )
        print(f"  Gespeichert: {sonnet_path}")

    # --- 3) Vergleichsdokument (ein weiterer Aufruf: „Vergleiche die beiden Audits“) ---
    compare_path = DOCS_DIR / "DEV_AGENT_REVIEW_VERGLEICH_Opus_vs_Sonnet.md"
    compare_prompt = """Du vergleichst zwei Architektur-Audits desselben Projekt-Kontexts (Schnittstellen, Sicherheit, Backup), einmal von Claude Opus 4.6, einmal von Claude Sonnet.

AUDIT OPUS 4.6:
---
""" + opus_text + """

---
AUDIT SONNET:
---
""" + sonnet_text + """

---
AUFGABE:
Erstelle ein kurzes Vergleichsdokument auf Deutsch:
1) Wo stimmen beide überein (Kernpunkte)?
2) Wo weichen sie ab (unterschiedliche Schwerpunkte oder Bewertungen)?
3) Welche Punkte hat nur Opus / nur Sonnet genannt?
4) Eine knappe Empfehlung: Für wen eignet sich welches Modell für solche Audits (Latenz, Tiefe, Kosten)?
Halte es auf 1–2 Seiten, strukturiert mit Überschriften."""

    print("Erstelle Vergleich (Opus vs. Sonnet) ...")
    try:
        compare_text = call_claude(
            client, MODEL_SONNET_PRIMARY if sonnet_model == MODEL_SONNET_PRIMARY else MODEL_SONNET_FALLBACK,
            "Du bist ein technischer Redakteur. Fasse präzise und neutral zusammen.",
            compare_prompt,
            max_tokens=4096,
        )
        compare_path.write_text(
            f"===== VERGLEICH: Claude Opus 4.6 vs. Sonnet =====\n\n{compare_text}\n",
            encoding="utf-8",
        )
        print(f"  Gespeichert: {compare_path}")
    except Exception as e:
        print(f"  Vergleich fehlgeschlagen: {e}")
        compare_path.write_text(f"# Vergleich – Fehler\n\n{e}\n", encoding="utf-8")

    print("Fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

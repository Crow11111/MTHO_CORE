"""
Brio-Kamerabildauswertung mit Gemini Vision.
Erkennt Person sichtbar ja/nein, Zustand (z.B. sitzend, stehend, Raum leer), und ob mehr Bilder nötig sind.
"""
import os
import json
import re
from typing import Optional
from loguru import logger
from dotenv import load_dotenv

load_dotenv("c:/CORE/.env")

# Optional: google-genai für Vision
try:
    from google import genai
    from google.genai import types
    _genai_available = bool(os.getenv("GEMINI_API_KEY"))
except Exception:
    _genai_available = False

# Bildanalyse (Bild → Text: Person?, Zustand?) = multimodale Textausgabemodelle (3.1 Pro, 3 Pro).
# Nicht verwechseln: "Nano Banana Pro" / Gemini 3 Pro Image = Multimodale generative Modelle für
# Bildgenerierung und -bearbeitung (Bild raus), nicht für schnelle Bildanalyse (Text raus).
# Fallback: gemini-3-pro-preview (Gemini 3 Pro, in AI Studio als "Gemini 3 Pro" gelistet).
GEMINI_VISION_MODEL = os.getenv("BRIO_VISION_MODEL", "gemini-3.1-pro-preview")
BRIO_VISION_FALLBACK = os.getenv("BRIO_VISION_FALLBACK", "gemini-3-pro-preview")

PROMPT_SINGLE = """Analysiere dieses Bild von einer Raumkamera (z.B. Schreibtisch/Büro).
Antworte NUR in diesem exakten Format (eine Zeile pro Punkt):
PERSON: ja oder nein
STATE: kurze Beschreibung (z.B. Person sitzend, Person stehend, Raum leer, Bild zu dunkel, unscharf)
NEED_MORE: ja oder nein (nur "ja" wenn du dir unsicher bist und ein weiteres Bild helfen würde)
"""

PROMPT_MULTI = """Du siehst mehrere Bilder nacheinander von derselben Raumkamera.
Fasse zusammen: Ist eine Person zu sehen? Welcher Zustand (z.B. Person sitzend, Raum leer)?
Antworte im Format:
PERSON: ja oder nein
STATE: kurze Beschreibung
"""


def _get_client():
    if not _genai_available:
        return None
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_frame(image_bytes: bytes, prompt: str = PROMPT_SINGLE) -> Optional[str]:
    """Einzelbild an Gemini Vision senden, Textantwort zurück. Bei Modellfehler Fallback (3 Pro)."""
    client = _get_client()
    if not client:
        logger.warning("GEMINI_API_KEY fehlt – Bildauswertung übersprungen")
        return None
    part_image = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    models_to_try = [GEMINI_VISION_MODEL]
    if BRIO_VISION_FALLBACK and BRIO_VISION_FALLBACK != GEMINI_VISION_MODEL:
        models_to_try.append(BRIO_VISION_FALLBACK)
    for model in models_to_try:
        if not model:
            continue
        try:
            response = client.models.generate_content(
                model=model,
                contents=[part_image, prompt],
            )
            if response and response.text:
                return response.text.strip()
            return None
        except Exception as e:
            err_str = str(e).upper()
            if "404" in err_str or "NOT_FOUND" in err_str or "no longer available" in err_str:
                logger.warning(f"Modell {model} nicht verfügbar, versuche Fallback {BRIO_VISION_FALLBACK}: {e}")
                continue
            logger.error(f"Gemini Vision Fehler ({model}): {e}")
            return None
    return None


def parse_analysis(text: str) -> dict:
    """Parst die Textantwort in person_visible, state, need_more."""
    out = {"person_visible": None, "state": "", "need_more": False, "raw": text}
    if not text:
        return out
    text_upper = text.upper()
    if "PERSON: JA" in text_upper or "PERSON:JA" in text_upper:
        out["person_visible"] = True
    elif "PERSON: NEIN" in text_upper or "PERSON:NEIN" in text_upper:
        out["person_visible"] = False
    if "STATE:" in text_upper:
        m = re.search(r"STATE:\s*(.+?)(?=\n|NEED_MORE|$)", text, re.IGNORECASE | re.DOTALL)
        if m:
            out["state"] = m.group(1).strip()[:200]
    if "NEED_MORE: JA" in text_upper or "NEED_MORE:JA" in text_upper or "NEED_MORE IMAGES" in text_upper:
        out["need_more"] = True
    return out


def analyze_and_parse(image_bytes: bytes) -> dict:
    """Bild analysieren und strukturiert zurückgeben."""
    text = analyze_frame(image_bytes, PROMPT_SINGLE)
    return parse_analysis(text or "")

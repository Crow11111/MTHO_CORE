"""
ATLAS Voice Assistant – Smart Command Parser
=============================================
Übersetzt natürliche Sprache in Home-Assistant-Aktionen.
Entity Resolution via Fuzzy-Match, hardcodierte Patterns + LLM-Fallback.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

# Optional: rapidfuzz für Fuzzy-Matching (Fallback: einfache Substring-Suche)
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


@dataclass
class HAAction:
    """Strukturierte HA-Aktion für Service-Aufruf."""

    domain: str
    service: str
    entity_id: str
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    source: str = "parser"  # "pattern" | "llm"


# Synonyme für Licht/Beleuchtung (Entity-Erkennung)
LIGHT_SYNONYMS = {"licht", "lampe", "beleuchtung", "leuchte", "birne"}

# Domain-Hinweise aus Schlüsselwörtern
DOMAIN_HINTS = {
    "lauter": "media_player",
    "leiser": "media_player",
    "lautstärke": "media_player",
    "volume": "media_player",
    "fernseher": "media_player",
    "heller": "light",
    "dunkler": "light",
    "helligkeit": "light",
    "farbe": "light",
    "temperatur": "climate",
    "heizung": "climate",
    "klima": "climate",
}


# Farbnamen → RGB (gängige Werte)
COLOR_MAP = {
    "rot": [255, 0, 0],
    "gruen": [0, 255, 0],
    "grün": [0, 255, 0],
    "blau": [0, 0, 255],
    "weiß": [255, 255, 255],
    "weiss": [255, 255, 255],
    "gelb": [255, 255, 0],
    "orange": [255, 165, 0],
    "lila": [128, 0, 128],
    "violett": [148, 0, 211],
    "türkis": [0, 206, 209],
    "tuerkis": [0, 206, 209],
    "rosa": [255, 192, 203],
    "warm": [255, 200, 150],
    "kalt": [200, 220, 255],
}


def _normalize_entity_name(name: str) -> str:
    """Normalisiert Entity-Namen für Vergleiche (Umlaute, Leerzeichen)."""
    t = (name or "").lower().strip()
    t = t.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    t = re.sub(r"\s+", "_", t)
    return t


def _build_entity_index(entities: list[dict]) -> dict[str, str]:
    """
    Erstellt Index: normalized_name / friendly_name → entity_id.
    entities: Liste von HA-State-Objekten (entity_id, attributes.friendly_name).
    """
    index: dict[str, str] = {}
    for e in entities or []:
        eid = e.get("entity_id") or ""
        if not eid:
            continue
        fname = (e.get("attributes") or {}).get("friendly_name") or ""
        # entity_id ohne Domain als Key (z.B. "regal" für light.regal)
        short_id = eid.split(".")[-1] if "." in eid else eid
        norm_short = _normalize_entity_name(short_id)
        norm_fname = _normalize_entity_name(fname)
        index[norm_short] = eid
        if norm_fname:
            index[norm_fname] = eid
        # Auch Teile des friendly_name (z.B. "Regal" aus "LED Regal")
        for part in norm_fname.split("_"):
            if len(part) >= 3:
                index[part] = eid
    return index


def _fuzzy_resolve_entity(
    query: str,
    entities: list[dict],
    entity_index: dict[str, str],
    min_score: int = 70,
) -> str | None:
    """
    Löst Query-String auf entity_id auf (Fuzzy-Match).
    Nutzt entity_index für exakte Treffer, rapidfuzz für ähnliche Namen.
    """
    qnorm = _normalize_entity_name(query)
    if not qnorm:
        return None

    # Exakter Index-Lookup
    if qnorm in entity_index:
        return entity_index[qnorm]

    # Substring-Match (ohne rapidfuzz)
    for key, eid in entity_index.items():
        if qnorm in key or key in qnorm:
            return eid

    # Fuzzy-Match mit rapidfuzz
    if HAS_RAPIDFUZZ:
        best_match: str | None = None
        best_score = 0
        candidates = set(entity_index.keys())
        for cand in candidates:
            score = fuzz.ratio(qnorm, cand)
            if score > best_score and score >= min_score:
                best_score = score
                best_match = entity_index[cand]
        return best_match

    return None


def _extract_percent(text: str) -> int | None:
    """Extrahiert Prozentwert (0–100) aus Text."""
    m = re.search(r"(\d{1,3})\s*%", text, re.IGNORECASE)
    if m:
        val = int(m.group(1))
        return min(100, max(0, val))
    return None


def _extract_temperature(text: str) -> float | None:
    """Extrahiert Temperatur in Grad Celsius."""
    m = re.search(r"(\d{1,2}(?:[.,]\d+)?)\s*(?:grad|°|c)?", text, re.IGNORECASE)
    if m:
        s = m.group(1).replace(",", ".")
        return float(s)
    return None


def _extract_color(text: str) -> list[int] | None:
    """Extrahiert Farbe aus Text (Farbname → RGB)."""
    t = text.lower()
    for name, rgb in COLOR_MAP.items():
        if name in t:
            return rgb
    return None


def _try_hardcoded_patterns(
    text: str,
    entities: list[dict],
    entity_index: dict[str, str],
) -> HAAction | None:
    """
    Versucht hardcodierte Regex-Patterns zu matchen.
    Returns HAAction oder None wenn kein Match.
    """
    t = text.strip().lower()
    if not t:
        return None

    # --- Pattern: [entity] aus / an / ein / off ---
    off_pattern = re.compile(
        r"(?:mach\s+)?(?:das\s+)?(?:die\s+)?(.+?)\s+(?:aus|off)\b",
        re.IGNORECASE,
    )
    on_pattern = re.compile(
        r"(?:mach\s+)?(?:das\s+)?(?:die\s+)?(.+?)\s+(?:an|ein|on)\b",
        re.IGNORECASE,
    )
    toggle_pattern = re.compile(
        r"(?:mach\s+)?(?:das\s+)?(?:die\s+)?(.+?)\s+(?:um|toggle|umschalten)\b",
        re.IGNORECASE,
    )

    for pattern, service in [
        (off_pattern, "turn_off"),
        (on_pattern, "turn_on"),
        (toggle_pattern, "toggle"),
    ]:
        m = pattern.search(t)
        if m:
            entity_ref = m.group(1).strip()
            # Synonyme entfernen (z.B. "Licht Regal" -> "Regal")
            for syn in LIGHT_SYNONYMS:
                entity_ref = re.sub(rf"\b{syn}\s+", "", entity_ref, flags=re.I).strip()
                entity_ref = re.sub(rf"\s+{syn}\b", "", entity_ref, flags=re.I).strip()
            eid = _fuzzy_resolve_entity(entity_ref, entities, entity_index)
            if eid:
                domain = eid.split(".")[0] if "." in eid else "light"
                return HAAction(
                    domain=domain,
                    service=service,
                    entity_id=eid,
                    data={},
                    confidence=0.95,
                    source="pattern",
                )

    # --- Pattern: [entity] [prozent]% helligkeit ---
    bright_pattern = re.compile(
        r"(.+?)\s+(\d{1,3})\s*%\s*(?:helligkeit|hell|brightness)?",
        re.IGNORECASE,
    )
    m = bright_pattern.search(t)
    if m:
        entity_ref = m.group(1).strip()
        pct = _extract_percent(text)
        if pct is not None:
            for syn in LIGHT_SYNONYMS:
                entity_ref = re.sub(rf"\b{syn}\s+", "", entity_ref, flags=re.I).strip()
            eid = _fuzzy_resolve_entity(entity_ref, entities, entity_index)
            if eid:
                return HAAction(
                    domain="light",
                    service="turn_on",
                    entity_id=eid,
                    data={"brightness_pct": pct},
                    confidence=0.95,
                    source="pattern",
                )

    # --- Pattern: Lautstärke [entity] um [x]% erhöhen/verringern ---
    vol_pattern = re.compile(
        r"lautstärke\s+(.+?)\s+um\s+(\d{1,3})\s*%\s+(erhöhen|verringern|erhoehen|verringern)",
        re.IGNORECASE,
    )
    m = vol_pattern.search(t)
    if m:
        entity_ref = m.group(1).strip()
        delta = int(m.group(2))
        direction = m.group(3).lower()
        if "verringern" in direction or "leiser" in t:
            delta = -delta
        eid = _fuzzy_resolve_entity(entity_ref, entities, entity_index)
        if eid and eid.startswith("media_player."):
            # volume_set erwartet 0.0–1.0; wir nutzen volume_up/volume_down mit steps
            # Für "um X% erhöhen" -> volume_up mit repeat
            return HAAction(
                domain="media_player",
                service="volume_up" if delta > 0 else "volume_down",
                entity_id=eid,
                data={"entity_id": eid},
                confidence=0.9,
                source="pattern",
            )

    # --- Pattern: [entity] [farbe] ---
    for color_name in COLOR_MAP:
        if color_name in t:
            # Entity vor der Farbe
            parts = t.split(color_name)[0].strip().split()
            entity_ref = " ".join(parts[-2:]) if len(parts) >= 2 else (parts[0] if parts else "")
            for syn in LIGHT_SYNONYMS:
                entity_ref = re.sub(rf"\b{syn}\s+", "", entity_ref, flags=re.I).strip()
            if not entity_ref:
                entity_ref = "deckenlampe"  # Default
            eid = _fuzzy_resolve_entity(entity_ref, entities, entity_index)
            if eid:
                rgb = COLOR_MAP[color_name]
                return HAAction(
                    domain="light",
                    service="turn_on",
                    entity_id=eid,
                    data={"rgb_color": rgb},
                    confidence=0.9,
                    source="pattern",
                )

    # --- Pattern: Temperatur [entity] auf [x] Grad ---
    temp_pattern = re.compile(
        r"temperatur\s+(.+?)\s+auf\s+(\d{1,2}(?:[.,]\d+)?)\s*(?:grad|°)?",
        re.IGNORECASE,
    )
    m = temp_pattern.search(t)
    if m:
        entity_ref = m.group(1).strip()
        temp = _extract_temperature(text)
        if temp is not None:
            eid = _fuzzy_resolve_entity(entity_ref, entities, entity_index)
            if eid and (eid.startswith("climate.") or "heizung" in t or "thermostat" in t):
                return HAAction(
                    domain="climate",
                    service="set_temperature",
                    entity_id=eid,
                    data={"temperature": temp},
                    confidence=0.9,
                    source="pattern",
                )

    # --- Kurzform: "Regal an" / "Deckenlampe aus" (ohne "mach das") ---
    simple = re.match(r"^(.+?)\s+(an|aus|ein|off)$", t)
    if simple:
        entity_ref = simple.group(1).strip()
        action_word = simple.group(2).lower()
        for syn in LIGHT_SYNONYMS:
            entity_ref = re.sub(rf"\b{syn}\s+", "", entity_ref, flags=re.I).strip()
        eid = _fuzzy_resolve_entity(entity_ref, entities, entity_index)
        if eid:
            service = "turn_off" if action_word in ("aus", "off") else "turn_on"
            domain = eid.split(".")[0] if "." in eid else "light"
            return HAAction(
                domain=domain,
                service=service,
                entity_id=eid,
                data={},
                confidence=0.9,
                source="pattern",
            )

    return None


def _llm_fallback(text: str, entities: list[dict], entity_index: dict[str, str]) -> HAAction | None:
    """
    LLM-Fallback: Ollama/Gemini Triage für unbekannte Befehle.
    Structured Output: {domain, service, entity_id, data}
    """
    try:
        from pydantic import BaseModel, Field

        class HAActionSchema(BaseModel):
            domain: str = Field(description="HA domain, e.g. light, media_player, climate")
            service: str = Field(description="HA service, e.g. turn_on, turn_off, volume_set")
            entity_id: str = Field(description="Full entity_id, e.g. light.regal")
            data: dict = Field(default_factory=dict, description="Service data dict")

        # Entity-Liste für Kontext (nur light, media_player, climate)
        relevant = [
            e.get("entity_id", "")
            for e in (entities or [])
            if (e.get("entity_id") or "").split(".")[0] in ("light", "media_player", "climate")
        ][:50]

        entity_list = "\n".join(relevant) if relevant else "light.regal, light.deckenlampe, media_player.fernseher"

        import os
        from dotenv import load_dotenv

        load_dotenv()

        # Bevorzuge Ollama (lokal)
        ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import SystemMessage, HumanMessage

            llm = ChatOllama(
                model=ollama_model,
                base_url=ollama_url,
                temperature=0.1,
            ).with_structured_output(HAActionSchema)

            prompt = (
                "Du bist ein Smart-Home-Befehlsparser. Übersetze den Benutzerbefehl in eine HA-Aktion.\n\n"
                f"Verfügbare Entities (wähle die passendste):\n{entity_list}\n\n"
                "Regeln:\n"
                "- domain: light, media_player, climate, switch\n"
                "- service: turn_on, turn_off, toggle, volume_set, set_temperature\n"
                "- entity_id: exakte ID aus der Liste\n"
                "- data: z.B. {brightness_pct: 80} oder {temperature: 21}\n\n"
                f"Befehl: \"{text}\""
            )
            result = llm.invoke([SystemMessage(content=prompt)])
            if result and result.entity_id:
                return HAAction(
                    domain=result.domain,
                    service=result.service,
                    entity_id=result.entity_id,
                    data=result.data or {},
                    confidence=0.7,
                    source="llm",
                )
        except Exception as e:
            logger.warning(f"Ollama LLM-Fallback fehlgeschlagen: {e}")

        # Fallback: Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                llm = ChatGoogleGenerativeAI(
                    model=os.getenv("GEMINI_HEAVY_MODEL", "gemini-3.1-pro-preview"),
                    google_api_key=gemini_key,
                    temperature=0.1,
                ).with_structured_output(HAActionSchema)

                prompt = (
                    f"Parse this smart home command into HA action. Entities: {entity_list}\n\n"
                    f"Command: \"{text}\"\n\n"
                    "Return domain, service, entity_id, data."
                )
                result = llm.invoke([HumanMessage(content=prompt)])
                if result and result.entity_id:
                    return HAAction(
                        domain=result.domain,
                        service=result.service,
                        entity_id=result.entity_id,
                        data=result.data or {},
                        confidence=0.7,
                        source="llm",
                    )
            except Exception as e:
                logger.warning(f"Gemini LLM-Fallback fehlgeschlagen: {e}")

    except ImportError as e:
        logger.warning(f"LLM-Fallback nicht verfügbar: {e}")

    return None


def parse_command(
    text: str,
    entities: list[dict] | None = None,
    *,
    skip_llm_fallback: bool = False,
) -> HAAction | None:
    """
    Haupt-API: Parst natürliche Sprache in HAAction.

    Args:
        text: Benutzereingabe (z.B. "Regal 80% Helligkeit", "Deckenlampe aus")
        entities: Liste HA-States von get_states(). Wenn None, wird versucht
                  über HomeAssistantClient zu laden (async-Kontext nötig).
        skip_llm_fallback: Wenn True, wird LLM-Fallback übersprungen (für Tests).

    Returns:
        HAAction oder None wenn kein Match.
    """
    text = (text or "").strip()
    if not text:
        return None

    if entities is None:
        entities = []

    entity_index = _build_entity_index(entities)

    # 1. Hardcodierte Patterns
    action = _try_hardcoded_patterns(text, entities, entity_index)
    if action:
        logger.info(f"Smart Parser: Pattern-Match -> {action.domain}.{action.service} {action.entity_id}")
        return action

    # 2. LLM-Fallback (überspringbar für schnelle Tests)
    if skip_llm_fallback:
        return None
    action = _llm_fallback(text, entities, entity_index)
    if action:
        logger.info(f"Smart Parser: LLM-Fallback -> {action.domain}.{action.service} {action.entity_id}")
        return action

    logger.warning(f"Smart Parser: Kein Match für '{text}'")
    return None


async def parse_command_async(text: str, ha_client=None) -> HAAction | None:
    """
    Async-Variante: Lädt Entities von HA, wenn nicht übergeben.
    """
    entities = None
    if ha_client and hasattr(ha_client, "get_states"):
        try:
            entities = await ha_client.get_states()
        except Exception as e:
            logger.warning(f"get_states fehlgeschlagen: {e}")

    return parse_command(text, entities)

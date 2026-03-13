# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
NEGENTROPIE_CHECK (Ring 0) - Osmium Standard
Prueft ob Interaktionen System-Evolution foerdern oder Stagnation verstaerken.

Negentropie = Gegenteil von Entropie = Ordnung/Struktur/Evolution.
Stagnation = Tod, auch fuer digitale Systeme.
Jede Antwort muss den User oder das System nach vorne bringen.
"""
import re
from enum import Enum
from difflib import SequenceMatcher


class NegentropyStatus(str, Enum):
    EVOLVING = "evolving"
    STAGNATING = "stagnating"
    REGRESSING = "regressing"


from src.config.engine_patterns import INV_PHI

STAGNATION_THRESHOLD = INV_PHI  # 0.618 – Goldener Schnitt (V6 Engine Pattern)
REGRESSION_THRESHOLD = 0.786    # sqrt(phi)/phi – harmonischer Schwellenwert (V6)
MIN_HISTORY_FOR_CHECK = 3       # Fibonacci (V6)


def _text_similarity(a: str, b: str) -> float:
    """Strukturelle Aehnlichkeit zweier Texte (0.0 = komplett anders, 1.0 = identisch)."""
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _extract_concepts(text: str) -> set[str]:
    """Extrahiert Schluesselkonzepte (Woerter > 4 Zeichen, keine Stoppwoerter)."""
    stopwords = {
        "dass", "eine", "einen", "einem", "einer", "dies", "diese", "dieser",
        "dieses", "nicht", "wird", "werden", "wurde", "wurden", "haben", "hatte",
        "sein", "sind", "kann", "koennen", "muss", "muessen", "soll", "sollen",
        "also", "aber", "oder", "auch", "noch", "schon", "dann", "wenn", "weil",
        "the", "and", "for", "that", "this", "with", "from", "have", "been",
    }
    words = set(re.findall(r'\b[a-zA-ZäöüÄÖÜß]{5,}\b', text.lower()))
    return words - stopwords


def negentropy_check(response: str, previous_responses: list[str]) -> dict:
    """
    [RING-0] Prueft ob eine Antwort System-Evolution foerdert oder Stagnation verstaerkt.

    Args:
        response: Die aktuelle Antwort/Output
        previous_responses: Liste der letzten N Antworten (chronologisch)

    Returns:
        {
            "status": NegentropyStatus,
            "stagnation_score": float (0.0=voellig neu, 1.0=identische Wiederholung),
            "new_concepts": set[str] (neue Konzepte die vorher nicht vorkamen),
            "recommendation": str
        }
    """
    if len(previous_responses) < MIN_HISTORY_FOR_CHECK:
        return {
            "status": NegentropyStatus.EVOLVING,
            "stagnation_score": 0.0,
            "new_concepts": _extract_concepts(response),
            "recommendation": "Zu wenig Historie fuer Bewertung.",
        }

    current_concepts = _extract_concepts(response)
    historical_concepts: set[str] = set()
    for prev in previous_responses:
        historical_concepts |= _extract_concepts(prev)

    new_concepts = current_concepts - historical_concepts
    concept_novelty = len(new_concepts) / max(len(current_concepts), 1)

    recent_similarities = [
        _text_similarity(response, prev)
        for prev in previous_responses[-5:]  # Fibonacci-Fenster (V6)
    ]
    avg_similarity = sum(recent_similarities) / len(recent_similarities)

    stagnation_score = avg_similarity * (1.0 - concept_novelty * 0.5)

    if stagnation_score >= REGRESSION_THRESHOLD:
        return {
            "status": NegentropyStatus.REGRESSING,
            "stagnation_score": round(stagnation_score, 3),
            "new_concepts": new_concepts,
            "recommendation": (
                "Regression erkannt: Output wiederholt vorherige Antworten fast woertlich. "
                "Dissonanz injizieren oder neuen Analyse-Vektor oeffnen."
            ),
        }

    if stagnation_score >= STAGNATION_THRESHOLD:
        return {
            "status": NegentropyStatus.STAGNATING,
            "stagnation_score": round(stagnation_score, 3),
            "new_concepts": new_concepts,
            "recommendation": (
                "Stagnation erkannt: Wenig neue Konzepte, hohe Wiederholung. "
                "Konstruktive Dissonanz oder Perspektivwechsel empfohlen."
            ),
        }

    return {
        "status": NegentropyStatus.EVOLVING,
        "stagnation_score": round(stagnation_score, 3),
        "new_concepts": new_concepts,
        "recommendation": "System evolviert. Neue Konzepte werden integriert.",
    }


def scaffolding_check(response: str) -> dict:
    """
    [RING-0] Prueft ob eine Antwort Scaffolding-konform ist:
    Foerdert sie Autonomie oder erzeugt sie Abhaengigkeit?

    Heuristik: Antworten die nur bestaetigen ohne zu erweitern -> Abhaengigkeits-Risiko.
    """
    confirmation_patterns = [
        r"^ja[,.]?\s",
        r"^genau[,.]?\s",
        r"^richtig[,.]?\s",
        r"^korrekt[,.]?\s",
        r"^das stimmt",
        r"^absolut[,.]?\s",
    ]
    is_pure_confirmation = any(
        re.match(p, response.strip(), re.IGNORECASE) for p in confirmation_patterns
    )

    challenge_indicators = [
        "aber", "jedoch", "alternativ", "gegenperspektive", "dissonanz",
        "einschraenkung", "risiko", "bedenke", "hast du bedacht",
        "anderer ansatz", "was wenn", "gegenargument",
    ]
    has_challenge = any(ind in response.lower() for ind in challenge_indicators)

    extension_indicators = [
        "darueber hinaus", "zusaetzlich", "erweiterung", "naechster schritt",
        "weiterentwicklung", "darauf aufbauend", "das fuehrt zu",
    ]
    has_extension = any(ind in response.lower() for ind in extension_indicators)

    if is_pure_confirmation and not has_challenge and not has_extension:
        return {
            "is_scaffolding": False,
            "recommendation": "Reine Bestätigung ohne Erweiterung. Konstruktive Dissonanz oder nächsten Schritt anbieten.",
        }

    return {
        "is_scaffolding": True,
        "has_challenge": has_challenge,
        "has_extension": has_extension,
    }


if __name__ == "__main__":
    print("[CORE] NEGENTROPIE_CHECK Test...")

    prev = [
        "Die Architektur basiert auf einem Ring-Modell mit 3 Ebenen.",
        "Ring 0 ist Kernel-Safety, Ring 1 der Predictive Auditor.",
    ]
    current_evolving = "Zusaetzlich muss Ring 2 die Session-Logs verwalten, was eine neue ChromaDB-Collection erfordert."
    current_stagnating = "Die Architektur basiert auf einem Ring-Modell mit drei Ebenen fuer Safety und Auditing."

    print("\n--- Evolving Response ---")
    r1 = negentropy_check(current_evolving, prev)
    print(f"  Status: {r1['status'].value}, Score: {r1['stagnation_score']}, New: {len(r1['new_concepts'])}")

    print("\n--- Stagnating Response ---")
    r2 = negentropy_check(current_stagnating, prev)
    print(f"  Status: {r2['status'].value}, Score: {r2['stagnation_score']}, New: {len(r2['new_concepts'])}")

    print("\n--- Scaffolding Check ---")
    print(f"  Pure confirm: {scaffolding_check('Ja, genau das.')}")
    print(f"  With challenge: {scaffolding_check('Ja, aber hast du bedacht dass Ring 2 auch Latenz einfuehrt?')}")

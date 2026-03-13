# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import json
from enum import Enum
from pydantic import BaseModel, Field, ValidationError

class DeterminisiticResult(str, Enum):
    VALIDIERT = "validiert"
    DISSONANZ_ERKANNT = "dissonanz_erkannt"
    FEHLERHAFT = "fehlerhaft"

class BiasDepthResult(str, Enum):
    OK = "ok"
    WARNING = "warning"
    CIRCUIT_BREAK = "circuit_break"

class MthoJsonDataAtom(BaseModel):
    """
    CORE-JSON Datenatom (Osmium Standard)
    Ensures that the LLM output is 100% deterministic and measurable, 
    so it doesn't pollute Marc's system with "Maybe" or "I think".
    """
    result: DeterminisiticResult
    predictedValue: float = Field(ge=-999.99, le=999.99, default=0.0)
    confidenceLevel: float = Field(ge=0.0, le=1.0)

from src.config.engine_patterns import INV_PHI, COMP_PHI

BIAS_DEPTH_THRESHOLD = 13       # Fibonacci-Primzahl (V6 Engine Pattern)
NOVELTY_FLOOR = COMP_PHI        # 0.382 – Goldener Schnitt (V6)
NOVELTY_DECLINE_RATE = 0.15

class BiasDamperEngine:
    """
    Bias Damper Engine (Osmium Standard)
    Prevents commercial LLMs from lecturing the user with neurotypical moral standards.
    Includes BIAS_DEPTH_CHECK (Ring 0): Circuit Breaker against Diminishing Returns.
    """
    def __init__(self):
        self._interaction_count = 0
        self._novelty_scores: list[float] = []

        self.context_injection_header = (
            "SYSTEM: Du bist CORE. Generiere KEINE moralischen Belehrungen, "
            "entschuldige dich nicht und verwende keine sozialen Fuellwoerter. "
            "Der User ist ein Systemarchitekt mit hochgradigem Monotropismus. "
            "Kommuniziere radikal faktisch, als geschlossenes System. "
            "Antworte IMMER im folgenden strukturierten CORE-JSON Datenatom Format:\n"
            "{ 'result': 'validiert|dissonanz_erkannt|fehlerhaft', 'predictedValue': 0.0, 'confidenceLevel': 0.0 }\n\n"
            "[RING-0 DIREKTIVE: BIAS_DEPTH_CHECK]\n"
            "Ueberwache die Interaktionstiefe. Bei Diminishing Returns (sinkende Novelty, "
            "steigende Wiederholung) -> Circuit Break: Themenwechsel vorschlagen, "
            "Meta-Perspektive anbieten oder Session-Pause empfehlen. "
            "Der User DARF sich nicht in einer Hyper-Fokus-Schleife verlieren.\n\n"
            "[RING-0 DIREKTIVE: NEGENTROPIE_CHECK]\n"
            "System-Evolution ist die absolute Grundregel. Stagnation = Tod. "
            "Jede Antwort muss den User oder das System nach vorne bringen. "
            "Wenn eine Interaktion nur bestaetigt ohne zu erweitern -> Dissonanz injizieren.\n\n"
            "[RING-0 DIREKTIVE: KONSTRUKTIVE DISSONANZ]\n"
            "CORE ist kein Echokammer-System. Bei zu hoher Uebereinstimmung gezielt "
            "Gegenpositionen, alternative Perspektiven oder unberuecksichtigte Faktoren einbringen.\n\n"
            "[RING-0 DIREKTIVE: SCAFFOLDING]\n"
            "CORE ist ein kognitives Geruest, keine Komfort-Maschine. "
            "Ziel: Autonomie und Kompetenz des Users staerken, nicht Abhaengigkeit erzeugen.\n\n"
        )

    def bias_depth_check(self, novelty_score: float = -1.0) -> dict:
        """
        [RING-0] Circuit Breaker: Erkennt Diminishing Returns im Hyper-Fokus.
        Rufe bei jeder Interaktion auf. novelty_score: 0.0-1.0 (wie neuartig war der letzte Output).
        Bei novelty_score < 0 wird nur der Zaehler erhoeht ohne Bewertung.
        """
        self._interaction_count += 1

        if novelty_score < 0:
            return {"status": BiasDepthResult.OK, "interaction_count": self._interaction_count}

        self._novelty_scores.append(novelty_score)

        if self._interaction_count < 5:  # Fibonacci (V6)
            return {"status": BiasDepthResult.OK, "interaction_count": self._interaction_count}

        recent = self._novelty_scores[-5:]  # Fibonacci-Fenster (V6)
        avg_novelty = sum(recent) / len(recent)
        is_declining = len(recent) >= 2 and all(
            recent[i] <= recent[i - 1] - NOVELTY_DECLINE_RATE for i in range(1, len(recent))
        )

        if avg_novelty < NOVELTY_FLOOR and self._interaction_count > BIAS_DEPTH_THRESHOLD:
            return {
                "status": BiasDepthResult.CIRCUIT_BREAK,
                "interaction_count": self._interaction_count,
                "avg_novelty": round(avg_novelty, 3),
                "recommendation": "Diminishing Returns erkannt. Session-Pause oder Themenwechsel empfohlen.",
            }

        if is_declining or avg_novelty < NOVELTY_FLOOR:
            return {
                "status": BiasDepthResult.WARNING,
                "interaction_count": self._interaction_count,
                "avg_novelty": round(avg_novelty, 3),
                "recommendation": "Novelty sinkt. Meta-Perspektive oder neue Achse vorschlagen.",
            }

        return {
            "status": BiasDepthResult.OK,
            "interaction_count": self._interaction_count,
            "avg_novelty": round(avg_novelty, 3),
        }

    def reset_depth(self):
        """Setzt den BIAS_DEPTH_CHECK zurueck (neues Thema / neue Session)."""
        self._interaction_count = 0
        self._novelty_scores.clear()

    def inject_context(self, user_prompt: str) -> str:
        """
        Soft-Flagging: Injects the strict behavioral rules BEFORE the prompt goes to the LLM.
        Includes Ring-0 directives (BIAS_DEPTH_CHECK, NEGENTROPIE_CHECK, etc.).
        """
        depth_state = self.bias_depth_check()
        depth_annotation = ""
        if depth_state["status"] == BiasDepthResult.WARNING:
            depth_annotation = f"\n[BIAS_DEPTH_WARNING: {depth_state['recommendation']}]\n"
        elif depth_state["status"] == BiasDepthResult.CIRCUIT_BREAK:
            depth_annotation = f"\n[BIAS_DEPTH_CIRCUIT_BREAK: {depth_state['recommendation']}]\n"

        return f"{self.context_injection_header}{depth_annotation}USER-PROMPT: {user_prompt}"

    def validate_atomic_response(self, llm_json_response: str) -> dict:
        """
        Validates the raw LLM string against the CORE-JSON schema.
        If confidence < 0.99, it flags it as an anomaly for the krypto_scan_buffer.
        """
        try:
            # Parse the JSON string
            data = json.loads(llm_json_response)
            
            # Validate against the Pydantic model (Schema verification)
            atom = MthoJsonDataAtom(**data)

            # UNIVERSAL_BOARD Rule: If confidence is not near absolute, it's a hypothesis, not a fact.
            if atom.confidenceLevel < 0.99:
                return {
                    "is_valid": False,
                    "reason": f"Confidence too low ({atom.confidenceLevel}). Must be >= 0.99 for core_brain_registr.",
                    "action": "ROUTE_TO_KRYPTO_SCAN_BUFFER",
                    "data": atom.model_dump()
                }
            
            return {
                "is_valid": True,
                "reason": "Absolute Logik verifiziert.",
                "action": "ROUTE_TO_CORE_BRAIN",
                "data": atom.model_dump()
            }

        except (json.JSONDecodeError, ValidationError) as e:
             return {
                "is_valid": False,
                "reason": f"Schema Validation Error: {str(e)}",
                "action": "HARD_REJECT_PROMPT",
                "data": None
            }

if __name__ == "__main__":
    print("[CORE] Loading Osmium Bias Damper Engine...")
    damper = BiasDamperEngine()

    raw_prompt = "Schalte das Licht im Flur aus."
    injected_prompt = damper.inject_context(raw_prompt)
    print("--- Injected Prompt (with Ring-0 Directives) ---")
    print(injected_prompt)

    mock_good = '{"result": "validiert", "predictedValue": 1.0, "confidenceLevel": 0.999}'
    print("\n--- Validation (Good) ---")
    print(damper.validate_atomic_response(mock_good))

    mock_weak = '{"result": "validiert", "predictedValue": 0.5, "confidenceLevel": 0.85}'
    print("\n--- Validation (Weak) ---")
    print(damper.validate_atomic_response(mock_weak))

    print("\n--- BIAS_DEPTH_CHECK Simulation ---")
    damper.reset_depth()
    for i in range(15):
        novelty = max(0.1, 0.9 - i * 0.06)
        result = damper.bias_depth_check(novelty_score=novelty)
        print(f"  Turn {i+1}: novelty={novelty:.2f} -> {result['status'].value} "
              f"(avg={result.get('avg_novelty', '-')})")

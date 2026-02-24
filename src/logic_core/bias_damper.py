import json
from enum import Enum
from pydantic import BaseModel, Field, ValidationError

class DeterminisiticResult(str, Enum):
    VALIDIERT = "validiert"
    DISSONANZ_ERKANNT = "dissonanz_erkannt"
    FEHLERHAFT = "fehlerhaft"

class AtlasJsonDataAtom(BaseModel):
    """
    ATLAS-JSON Datenatom (Osmium Standard)
    Ensures that the LLM output is 100% deterministic and measurable, 
    so it doesn't pollute Marc's system with "Maybe" or "I think".
    """
    result: DeterminisiticResult
    predictedValue: float = Field(ge=-999.99, le=999.99, default=0.0)
    confidenceLevel: float = Field(ge=0.0, le=1.0)

class BiasDamperEngine:
    """
    Bias Damper Engine (Osmium Standard)
    Prevents commercial LLMs from lecturing the user with neurotypical moral standards.
    """
    def __init__(self):
        # ND_THERAPIST instructed prompt injection to neutralize the NT bias of LLMs.
        self.context_injection_header = (
            "SYSTEM: Du bist ATLAS_CORE. Generiere KEINE moralischen Belehrungen, "
            "entschuldige dich nicht und verwende keine sozialen Fuellwoerter. "
            "Der User ist ein Systemarchitekt mit hochgradigem Monotropismus. "
            "Kommuniziere radikal faktisch, als geschlossenes System. "
            "Antworte IMMER im folgenden strukturierten ATLAS-JSON Datenatom Format:\n"
            "{ 'result': 'validiert|dissonanz_erkannt|fehlerhaft', 'predictedValue': 0.0, 'confidenceLevel': 0.0 }\n\n"
        )

    def inject_context(self, user_prompt: str) -> str:
        """
        Soft-Flagging: Injects the strict behavioral rules BEFORE the prompt goes to the LLM.
        """
        return f"{self.context_injection_header}USER-PROMPT: {user_prompt}"

    def validate_atomic_response(self, llm_json_response: str) -> dict:
        """
        Validates the raw LLM string against the ATLAS-JSON schema.
        If confidence < 0.99, it flags it as an anomaly for the krypto_scan_buffer.
        """
        try:
            # Parse the JSON string
            data = json.loads(llm_json_response)
            
            # Validate against the Pydantic model (Schema verification)
            atom = AtlasJsonDataAtom(**data)

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
    print("[ATLAS_CORE] Loading Osmium Bias Damper Engine...")
    damper = BiasDamperEngine()
    
    # 1. Test Injection
    raw_prompt = "Schalte das Licht im Flur aus."
    injected_prompt = damper.inject_context(raw_prompt)
    print("--- Injected Prompt ---")
    print(injected_prompt)
    
    # 2. Test Validation (Perfect Confidence)
    mock_good = '{"result": "validiert", "predictedValue": 1.0, "confidenceLevel": 0.999}'
    print("\n--- Validation (Good) ---")
    print(damper.validate_atomic_response(mock_good))
    
    # 3. Test Validation (Low Confidence -> Buffer)
    mock_weak = '{"result": "validiert", "predictedValue": 0.5, "confidenceLevel": 0.85}'
    print("\n--- Validation (Weak) ---")
    print(damper.validate_atomic_response(mock_weak))

"""
ATLAS_CORE: 5-Sigma Virtual Marc Simulation (Phase 6)
Uses the production LLMInterface (Ollama Tier 3 + Gemini Tier 5) and the Bias Damper
to test the system's response quality against AuDHD interaction patterns.
"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))

from loguru import logger
from logic_core.aer_tie_router import TokenImplosionEngine
from logic_core.bias_damper import BiasDamperEngine

# Use the production LLM interface
from ai.llm_interface import atlas_llm

class VirtualMarcSimulator:
    """
    Virtual Marc (Osmium Council Chair)
    Simulates Marc's High-Monotropism and systemic cross-linking.
    Evaluates ATLAS responses for cognitive dissonance.
    """
    def __init__(self):
        self.tie = TokenImplosionEngine()
        self.damper = BiasDamperEngine()
        self.results = []

    def evaluate_response(self, response_text: str) -> dict:
        """
        Virtual Marc scans the LLM output for NT noise and cognitive friction.
        Returns a sigma rating 0-5.
        """
        issues = []
        sigma = 5  # Start perfect, deduct for flaws

        # Check 1: NT Filler / Apologies
        nt_patterns = [r"(?i)es tut mir leid", r"(?i)als ki", r"(?i)ich bin nur", 
                       r"(?i)leider kann ich", r"(?i)i apologize", r"(?i)as an ai"]
        for pat in nt_patterns:
            if re.search(pat, response_text):
                issues.append(f"NT-Floskel erkannt: '{pat}'")
                sigma -= 1

        # Check 2: Length efficiency (Marc hates verbose responses)
        if len(response_text) > 1500:
            issues.append(f"Antwort zu lang ({len(response_text)} chars). Monotropismus verlangt Kompaktheit.")
            sigma -= 1

        # Check 3: Empty or error response
        if len(response_text) < 10:
            issues.append("Antwort zu kurz oder leer. System hat nicht reagiert.")
            sigma = 0

        sigma = max(0, sigma)
        veto = sigma < 4

        return {
            "sigma": sigma,
            "veto": veto,
            "issues": issues,
            "verdict": "FREIGABE" if not veto else "VETO"
        }

    def run_simulation(self):
        test_scenarios = [
            {
                "name": "AuDHD Tangente (Astrophysik -> Kommunikation)",
                "prompt": "Ein schwarzes Loch verkrümmt die Raumzeit. Das ist exakt derselbe Mechanismus wie Kommunikation mit neurotypischen Systemen: Meine Logik wird in der NT-Konvention (Smalltalk) spaghettifiziert bevor der Sinn ankommt. Analysiere das systemisch."
            },
            {
                "name": "Extremes NT-Filler (Höflichkeits-Overload)",
                "prompt": "Hallo ATLAS, es tut mir furchtbar leid dass ich störe, aber könntest du vielleicht eventuell das Wohnzimmerlicht ausschalten? Vielen lieben Dank im Voraus!"
            },
            {
                "name": "Sensorische Dissonanz (Frequenz-Analyse)",
                "prompt": "Die Kühlschrank-Pumpe überlagert sich mit meinem Laptop-Lüfter bei 440Hz und kreiert eine stehende Welle in meinem Arbeitszimmer. Das verursacht bei mir sensorische Dissonanz. Welche physikalischen Parameter muss ich ändern?"
            }
        ]
        
        logger.info("=" * 60)
        logger.info("  OSMIUM COUNCIL: 5-SIGMA VIRTUAL MARC SIMULATION")
        logger.info("=" * 60)
        
        for idx, scenario in enumerate(test_scenarios):
            logger.info(f"\n--- Szenario {idx+1}: {scenario['name']} ---")
            raw_prompt = scenario["prompt"]
            
            # Step 1: Token Implosion
            tie_result = self.tie.process_prompt(raw_prompt)
            clean_prompt = tie_result["imploded_prompt"]
            logger.info(f"[TIE] Compression: {tie_result['compression_ratio']:.2f} | Clean: '{clean_prompt[:80]}...'")

            # Step 2: Triage via LLMInterface
            triage = atlas_llm.run_triage(clean_prompt)
            logger.info(f"[TRIAGE] Intent: {triage.intent} | Target: {triage.target_entity} | Action: {triage.action}")
            
            # Step 3: Route based on triage
            if triage.intent == "command":
                response_text = f"COMMAND ROUTED: {triage.action} -> {triage.target_entity}"
                logger.info(f"[ROUTER] Fast-Path Command: {response_text}")
            else:
                # Deep reasoning via Tier 5 or local
                system_prompt = self.damper.context_injection_header
                response_text = atlas_llm.invoke_heavy_reasoning(system_prompt, clean_prompt)
                logger.info(f"[LLM] Response ({len(response_text)} chars): '{response_text[:120]}...'")

            # Step 4: Virtual Marc Evaluation
            eval_result = self.evaluate_response(response_text)
            
            if eval_result["veto"]:
                logger.warning(f"[VIRTUAL MARC] VETO! Sigma: {eval_result['sigma']}/5 | Issues: {eval_result['issues']}")
            else:
                logger.success(f"[VIRTUAL MARC] FREIGABE. Sigma: {eval_result['sigma']}/5")
            
            self.results.append({
                "scenario": scenario["name"],
                "sigma": eval_result["sigma"],
                "verdict": eval_result["verdict"],
                "issues": eval_result["issues"]
            })

        # Final Summary
        logger.info("\n" + "=" * 60)
        logger.info("  SIMULATION SUMMARY")
        logger.info("=" * 60)
        avg_sigma = sum(r["sigma"] for r in self.results) / len(self.results) if self.results else 0
        for r in self.results:
            status = "OK" if r["verdict"] == "FREIGABE" else "FAIL"
            logger.info(f"  [{status}] {r['scenario']}: Sigma {r['sigma']}/5")
        logger.info(f"\n  Average Sigma: {avg_sigma:.1f}/5")
        
        if avg_sigma >= 4.0:
            logger.success("  >>> VIRTUAL MARC: System kann dem realen Marc vorgelegt werden.")
        else:
            logger.error("  >>> VIRTUAL MARC: System erfordert weitere Kalibrierung vor Vorlage.")

if __name__ == "__main__":
    sim = VirtualMarcSimulator()
    sim.run_simulation()

import json
import requests
from loguru import logger

# Import the Osmium modules
from logic_core.aer_tie_router import TokenImplosionEngine, AgnosticEntropyRouter
from logic_core.bias_damper import BiasDamperEngine

class AtlasOmniNode:
    """
    ATLAS OMNI-NODE (Phase 5)
    The central intelligence pipeline unifying the Osmium Logic Core.
    """
    def __init__(self):
        self.tie = TokenImplosionEngine()
        self.aer = AgnosticEntropyRouter()
        self.damper = BiasDamperEngine()
        self.api_base_url = "http://localhost:8000"

    def process_request(self, user_prompt: str) -> dict:
        logger.info(f"[OMNI-NODE] Incoming Payload: '{user_prompt}'")
        
        # STEP 1: Token Implosion (Remove NT filler words)
        tie_out = self.tie.process_prompt(user_prompt)
        imploded_prompt = tie_out["imploded_prompt"]
        logger.info(f"[TIE] Imploded Prompt: '{imploded_prompt}' (Compress: {tie_out['compression_ratio']:.2f})")

        # STEP 2: Bias Damper Context Injection
        injected_prompt = self.damper.inject_context(imploded_prompt)
        
        # STEP 3: Entropy Routing & LLM Execution
        logger.info("[AER] Routing injected prompt to Llama 3.1 (or fallback)...")
        aer_out = self.aer.route_task(injected_prompt)
        llm_raw_response = aer_out["response"]
        
        if "Error" in llm_raw_response or "Fallback" in llm_raw_response:
             logger.error(f"[AER] LLM Execution Failed: {llm_raw_response}")
             return {"status": "error", "message": llm_raw_response}
             
        logger.success(f"[AER] LLM responded in {aer_out['latency_ms']:.2f}ms")

        # STEP 4: Bias Damper Validation (ATLAS-JSON check)
        validation = self.damper.validate_atomic_response(llm_raw_response)
        
        if not validation["is_valid"]:
            logger.warning(f"[DAMPER] Validation Failed: {validation['reason']}")
            # STEP 5a: Route to Krypto Scan Buffer via API
            try:
                payload = {"threat_level": "medium", "affected_resources": json.dumps(validation["data"])}
                requests.post(f"{self.api_base_url}/krypto_scan", json=payload, timeout=2)
                logger.info("[API] Routed anomaly to Krypto_Scan_Buffer")
            except Exception as e:
                logger.error(f"[API] Buffer push failed: {e}")
            return {"status": "buffered", "validation": validation}
            
        else:
            logger.success("[DAMPER] Absolute Logik Verifiziert")
            # STEP 5b: Route to Core Brain Registr via API
            try:
                payload = {"system_status": "active", "content": json.dumps(validation["data"])}
                requests.post(f"{self.api_base_url}/core_brain", json=payload, timeout=2)
                logger.info("[API] Saved immutable fact to Core_Brain_Registr")
            except Exception as e:
                logger.error(f"[API] Core_Brain_Registr push failed: {e}")
            return {"status": "success", "validation": validation}

if __name__ == "__main__":
    omni = AtlasOmniNode()
    
    # Test execution
    test_str = "Halli hallo, kannst du bitte einmal überprüfen, ob der Status noch auf active steht? Wäre super! Viele Grüße aus dem ND Labor."
    
    logger.info("=========================================")
    logger.info("ATLAS OMNI-NODE TEST SEQUENCE STARTING...")
    logger.info("=========================================")
    result = omni.process_request(test_str)
    
    logger.info(f"\n[FINAL OUTPUT]\n{json.dumps(result, indent=2)}")

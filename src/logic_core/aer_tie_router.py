import re
import math
import time
import requests
from typing import Dict, Any

class TokenImplosionEngine:
    """
    TIE (Token Implosion Engine) - Osmium Standard
    Filters out neurotypical conversational fluff to prevent cognitive friction.
    """
    def __init__(self):
        # Regex patterns representing NT "filler" or "social" semantics
        self.nt_filler_patterns = [
            r"Es tut mir leid, aber",
            r"kannst du bitte",
            r"Ich wuerde gerne",
            r"Vielen Dank im Voraus",
            r"Hallo ATLAS,",
            r"As an AI,",
            r"Als KI",
            r"Ich glaube,",
            r"vielleicht",
            r"eventuell"
        ]
        self.compiled_fillers = [re.compile(p, re.IGNORECASE) for p in self.nt_filler_patterns]
        self.seen_tokens = set()

    def process_prompt(self, raw_prompt: str) -> Dict[str, Any]:
        original_length = len(raw_prompt)
        imploded_prompt = raw_prompt

        # 1. Regex Cleanup (Remove NT fillers)
        for pattern in self.compiled_fillers:
            imploded_prompt = pattern.sub("", imploded_prompt)
        
        # 2. Basic Deduplication (Remove duplicate consecutive spaces/punctuation)
        imploded_prompt = re.sub(r'\s+', ' ', imploded_prompt).strip()
        imploded_prompt = re.sub(r'([?!.]){2,}', r'\1', imploded_prompt)

        imploded_length = len(imploded_prompt)
        compression_ratio = imploded_length / original_length if original_length > 0 else 1.0

        return {
            "imploded_prompt": imploded_prompt,
            "compression_ratio": compression_ratio,
            "original_length": original_length,
            "imploded_length": imploded_length
        }


class AgnosticEntropyRouter:
    """
    AER (Agnostic Entropy Router) - Osmium Standard
    Calculates Shannon Entropy of a task/prompt to route it to Node Alpha (Local) or Cloud API.
    """
    def __init__(self, local_api_url: str = "http://localhost:11434/api/generate"):
        self.local_api_url = local_api_url
        self.max_latency_ms = 1000 # UNIVERSAL_BOARD limits: >1s latency = Fallback required
        self.fallback_api_enabled = False # Cloud Fallback toggled off by default for security

    def calculate_shannon_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        
        # Calculate character frequency
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
            
        entropy = 0.0
        length = len(text)
        for count in freq.values():
            p_x = count / length
            entropy += - p_x * math.log2(p_x)
            
        return entropy

    def route_task(self, prompt: str) -> Dict[str, Any]:
        """
        Routes the prompt based on entropy. Low entropy (simple structural tasks) 
        and high entropy (complex reasoning) both default to the fast local Ollama Llama 3.1 
        unless latency is compromised.
        """
        entropy_val = self.calculate_shannon_entropy(prompt)
        
        # Local model routing via Ollama (Dreadnought GPU)
        payload = {
            "model": "llama3.1",
            "prompt": prompt,
            "stream": False
        }
        
        start_time = time.time()
        try:
            response = requests.post(self.local_api_url, json=payload, timeout=2.0)
            target_node = "Node Alpha (Local Ollama)"
            result_text = response.json().get('response', '') if response.status_code == 200 else "Error: Local API Failed"
        except requests.exceptions.RequestException:
            # Fallback triggered if Node Alpha fails or times out
            target_node = "Cloud API (Fallback)"
            result_text = "Fallback required. Local Node timeout or offline."

        latency_ms = (time.time() - start_time) * 1000

        return {
            "target_node": target_node,
            "entropy": entropy_val,
            "latency_ms": latency_ms,
            "response": result_text
        }

# --- Quick Test ---
if __name__ == "__main__":
    print("[ATLAS_CORE] Loading Osmium Logic Core (AER & TIE)...")
    tie = TokenImplosionEngine()
    aer = AgnosticEntropyRouter()

    test_prompt = "Hallo ATLAS, kannst du bitte den Status überprüfen? Ich glaube, das System ist offline."
    print(f"Original: {test_prompt}")
    
    tie_result = tie.process_prompt(test_prompt)
    print(f"Imploded: {tie_result['imploded_prompt']} (Ratio: {tie_result['compression_ratio']:.2f})")
    
    routing_result = aer.route_task(tie_result['imploded_prompt'])
    print(f"Routed to: {routing_result['target_node']} | Entropy: {routing_result['entropy']:.2f} | Latency: {routing_result['latency_ms']:.2f}ms")

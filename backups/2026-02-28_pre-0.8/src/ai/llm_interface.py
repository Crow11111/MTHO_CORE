import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger
from pydantic import BaseModel, Field

load_dotenv("C:/CORE/.env")

class TriageResult(BaseModel):
    intent: str = Field(description="The primary intent of the user. Options: 'command', 'deep_reasoning', 'chat', 'unknown'")
    target_entity: str = Field(description="If 'command', extract the target HA entity or domain, otherwise empty.", default="")
    action: str = Field(description="If 'command', the action to perform (e.g. turn_on, turn_off), otherwise empty.", default="")

class LLMInterface:
    def __init__(self):
        # Tier 3 / Tier 4 SLM (Ollama)
        ollama_base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        
        self.triage_slm = ChatOllama(
            model=ollama_model,
            base_url=ollama_base_url,
            temperature=0.1,  # Low temp for deterministic routing
        ).with_structured_output(TriageResult)

        # Tier 5 Heavy Reasoning Layer (Google Gemini)
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            self.heavy_llm = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_HEAVY_MODEL", "gemini-3.1-pro-preview"),
                google_api_key=gemini_api_key,
                temperature=0.7
            )
        else:
            self.heavy_llm = None
            logger.warning("GEMINI_API_KEY missing. Tier 5 (Heavy Layer) is degraded/disabled.")

    def run_triage(self, user_input: str) -> TriageResult:
        """
        Uses the local SLM to rapidly triage the semantic intent of the query.
        """
        user_input_lower = user_input.lower()
        logger.info(f"Running Triage on input: '{user_input}'")
        
        # --- FAST PATH LEXICAL TRIAGE ---
        # For the 20-30 most common commands, bypass the AI completely for 100% reliability & speed.
        fast_path_entities = {
            "bad": "light.bad",
            "badezimmer": "light.bad",
            "küche": "light.kueche",
            "kuche": "light.kueche",
            "kueche": "light.kueche",
            "flur": "light.flur",
            "deckenlampe": "light.deckenlampe",
            "wohnzimmer decke": "light.deckenlampe",
            "stehlampe": "light.stehlampe",
            "schreibtisch": "light.schreibtisch",
            "schreibtischlicht": "light.schreibtisch",
            "büro": "light.schreibtisch",
            "gaming": "light.schreibtisch",
            "regal": "light.regal",
            "sofa": "light.sofa",
        }
        
        # Check if any known entity is in the string
        found_entity = None
        for key, entity in fast_path_entities.items():
            if key in user_input_lower:
                found_entity = entity
                break
                
        if found_entity:
            # We found an entity. Now determine action.
            action = "turn_on" # default
            if "aus" in user_input_lower or "off" in user_input_lower:
                action = "turn_off"
            elif "toggle" in user_input_lower or "umschalten" in user_input_lower:
                action = "toggle"
                
            logger.info(f"Fast-Path Lexical Match: intent='command', target='{found_entity}', action='{action}'")
            return TriageResult(intent="command", target_entity=found_entity, action=action)
            
        # --- HEAVY LAYER / SLM TRIAGE ---
        try:
            prompt = (
                "You are an NLP routing agent for a smart home. You MUST output a strictly factual classification.\n\n"
                "RULES:\n"
                "1. If the user wants to turn something on/off/toggle, the 'intent' is ALWAYS 'command'.\n"
                "2. The 'action' MUST be one of: 'turn_on', 'turn_off', 'toggle'.\n"
                "3. The 'target_entity' MUST be EXACTLY chosen from this list:\n"
                "   - Bad / Badezimmer -> light.bad\n"
                "   - Küche / Kuche / Kueche -> light.kueche\n"
                "   - Deckenlampe / Wohnzimmer Decke -> light.deckenlampe\n"
                "   - Stehlampe -> light.stehlampe\n"
                "   - Flur -> light.flur\n"
                "If no entity explicitly matches, guess the closest one string from the right side of the arrows.\n\n"
                "EXAMPLE 1: 'Mach das Bad Licht an' -> intent='command', action='turn_on', target_entity='light.bad'\n"
                "EXAMPLE 2: 'Licht Küche aus' -> intent='command', action='turn_off', target_entity='light.kueche'\n\n"
                f"User Input: '{user_input}'"
            )
            result = self.triage_slm.invoke([
                SystemMessage(content=prompt)
            ])
            logger.info(f"Triage Result: {result}")
            return result
        except Exception as e:
            logger.error(f"SLM Triage failed: {e}")
            return TriageResult(intent="unknown")

    def invoke_heavy_reasoning(self, system_prompt: str, user_input: str) -> str:
        """
        Routes the task to the cloud/Tier 5 LLM for complex cognitive tasks.
        """
        if not self.heavy_llm:
            return "Fehler: Tier 5 (Heavy Reasoning) ist offline. Kein API Key."
            
        logger.info("Invoking Tier 5 Heavy Reasoning (Virtual Marc / Deep Analysis)...")
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            response = self.heavy_llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Tier 5 API Error: {e}")
            return f"Fehler in Tier 5: {e}"

# Singleton instance for the app
atlas_llm = LLMInterface()

# force reload

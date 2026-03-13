# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from loguru import logger
from pydantic import BaseModel, Field

# CORE-Kontext
from src.logic_core.z_vector_damper import shell_protected, RuntimeVetoException
from src.network.openclaw_client import send_message_to_agent_async, is_configured as is_oc_configured

load_dotenv("C:/CORE/.env")

class TriageResult(BaseModel):
    intent: str = Field(description="The primary intent of the user. Options: 'command', 'deep_reasoning', 'chat', 'unknown'")
    target_entity: str = Field(description="If 'command', extract the target HA entity or domain, otherwise empty.", default="")
    action: str = Field(description="If 'command', the action to perform (e.g. turn_on, turn_off), otherwise empty.", default="")

class ResilientLLMInterface:
    def __init__(self, ollama_model: str, ollama_base_url: str, local_fallback_url: Optional[str] = None):
        # Layer 2: Scout (Raspberry Pi)
        self.scout_llm = ChatOllama(
            model=ollama_model,
            base_url=ollama_base_url,
            temperature=0.7
        )
        # Layer 3: Local (Dreadnought GPU)
        self.local_llm = None
        if local_fallback_url:
            self.local_llm = ChatOllama(
                model=os.getenv("OLLAMA_HEAVY_MODEL", "llama3.1:latest"),
                base_url=local_fallback_url,
                temperature=0.7
            )
        logger.info(f"ResilientLLMInterface initialisiert. Primary: VPS, Secondary: Scout ({ollama_base_url}), Tertiary: Local ({local_fallback_url})")

    async def ainvoke(self, messages: list) -> str:
        """
        Versuchskette: VPS (OpenClaw) -> Scout (Ollama) -> Local (Ollama).
        Mit integriertem Fraktalem Padding (Axiom 0) vor dem Senden.
        """
        import math
        from src.api.middleware.friction_guard import FRICTION_STATE
        from src.config.core_state import BARYONIC_DELTA
        
        # --- Fraktales Padding (Die Helix) ---
        # Wir berechnen das Padding basierend auf der aktuellen Systemtemperatur
        current_temp = max(BARYONIC_DELTA, FRICTION_STATE.get("system_temperature", BARYONIC_DELTA))
        phase_shift = 1.0 - current_temp # Naeher an 1.0 = entspannt, tief = gestresst/hohes Padding
        
        base_delay_sec = 0.049
        k = 3.58
        padding_sec = base_delay_sec * math.exp(k * phase_shift)
        
        logger.info(f"[FRACTAL PADDING] System Temp: {current_temp:.3f} -> Phase Shift: {phase_shift:.3f}")
        logger.info(f"[FRACTAL PADDING] Wende topologisches Gewicht an... Warte {padding_sec:.2f}s (Helix Rotation)")
        await asyncio.sleep(padding_sec)

        # Formatiere Prompt für OpenClaw
        system_msg = next((m.content for m in messages if isinstance(m, SystemMessage)), "")
        human_msg = next((m.content for m in messages if isinstance(m, HumanMessage)), "")
        full_prompt = f"SYSTEM: {system_msg}\n\nUSER: {human_msg}" if system_msg else human_msg

        # --- LAYER 1: VPS (OpenClaw) ---
        if is_oc_configured():
            try:
                logger.info("[LLM-Resilience] L1: Versuche VPS-Call (OpenClaw)...")
                success, response = await asyncio.wait_for(
                    send_message_to_agent_async(full_prompt, agent_id="main", timeout=5.0),
                    timeout=5.5
                )
                
                if success and "LLM error" not in response and "expired" not in response.lower():
                    logger.info("[LLM-Resilience] L1 erfolgreich.")
                    return response
                logger.warning(f"[LLM-Resilience] L1 fehlgeschlagen oder ungültig: {response}")
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"[LLM-Resilience] L1 Timeout/Fehler: {e}")

        # --- LAYER 2: Scout (Ollama) ---
        try:
            logger.info("[LLM-Resilience] L2: Versuche Scout-Call (Ollama Edge)...")
            # Kürzerer Timeout für den Scout
            response = await asyncio.wait_for(self.scout_llm.ainvoke(messages), timeout=10.0)
            logger.info("[LLM-Resilience] L2 erfolgreich.")
            return response.content
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"[LLM-Resilience] L2 fehlgeschlagen: {e}")

        # --- LAYER 3: Local (Dreadnought GPU) ---
        if self.local_llm:
            try:
                logger.info("[LLM-Resilience] L3: Versuche lokalen Notfall-Fallback (Dreadnought GPU)...")
                response = await self.local_llm.ainvoke(messages)
                logger.info("[LLM-Resilience] L3 erfolgreich.")
                return response.content
            except Exception as e:
                logger.error(f"[LLM-Resilience] L3 fehlgeschlagen: {e}")

        return "KRITISCHER SYSTEMFEHLER: Alle 3 LLM-Layer (VPS, Scout, Local) offline."

class LLMInterface:
    def __init__(self):
        # Tier 3 / Tier 4 SLM (Ollama)
        ollama_base_url = os.getenv("OLLAMA_HOST", "http://192.168.178.54:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
        local_ollama_url = os.getenv("OLLAMA_LOCAL_HOST", "http://localhost:11434")

        self.triage_slm = ChatOllama(
            model=ollama_model,
            base_url=ollama_base_url,
            temperature=0.1,  # Low temp for deterministic routing
        ).with_structured_output(TriageResult)

        # Resilientes Heavy Layer (3-Tier)
        self.heavy_layer = ResilientLLMInterface(
            ollama_model=ollama_model,
            ollama_base_url=ollama_base_url,
            local_fallback_url=local_ollama_url
        )


    @shell_protected(estimated_tokens_per_call=800)
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
                "You are an NLP routing agent for a smart home and complex reasoning system. You MUST output a strictly factual classification.\n\n"
                "RULES:\n"
                "1. If the user wants to turn a smart home device on/off/toggle, the 'intent' is 'command'.\n"
                "2. If the user asks a complex question, provides architecture details, requests code, or writes a long text, the 'intent' MUST be 'deep_reasoning'.\n"
                "3. If 'command', the 'action' MUST be one of: 'turn_on', 'turn_off', 'toggle'.\n"
                "4. If 'command', the 'target_entity' MUST be EXACTLY chosen from this list:\n"
                "   - Bad / Badezimmer -> light.bad\n"
                "   - Küche / Kuche / Kueche -> light.kueche\n"
                "   - Deckenlampe / Wohnzimmer Decke -> light.deckenlampe\n"
                "   - Stehlampe -> light.stehlampe\n"
                "   - Flur -> light.flur\n"
                "If no entity explicitly matches, guess the closest one string from the right side of the arrows.\n\n"
                "EXAMPLE 1: 'Mach das Bad Licht an' -> intent='command', action='turn_on', target_entity='light.bad'\n"
                "EXAMPLE 2: 'Wir müssen die Architektur anpassen und Axiom 4 umschreiben' -> intent='deep_reasoning', action='', target_entity=''\n\n"
                f"User Input: '{user_input}'"
            )
            result = self.triage_slm.invoke([
                SystemMessage(content=prompt)
            ])
            logger.info(f"Triage Result: {result}")
            return result
        except RuntimeVetoException as e:
            logger.error(f"[Z-VETO] in Triage: {e}")
            return TriageResult(intent="unknown")
        except Exception as e:
            logger.error(f"SLM Triage failed: {e}")
            return TriageResult(intent="unknown")

    MAX_RESPONSE_TOKENS = 4096

    @shell_protected(estimated_tokens_per_call=4000)
    async def invoke_heavy_reasoning(self, system_prompt: str, user_input: str) -> str:
        """
        Routes the task to the cloud/Tier 5 LLM (OpenClaw) or local fallback.
        """
        logger.info("Invoking Resilient Tier 5 Heavy Reasoning...")
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            # Nutzt das resiliente Interface
            result = await self.heavy_layer.ainvoke(messages)

            word_count = len(result.split())
            if word_count > self.MAX_RESPONSE_TOKENS:
                logger.warning(
                    f"[LLM] Halluzinations-Bremse: {word_count} Woerter > {self.MAX_RESPONSE_TOKENS} Limit -- gekappt"
                )
                words = result.split()
                result = " ".join(words[: self.MAX_RESPONSE_TOKENS])

            return result
        except RuntimeVetoException as e:
            logger.error(f"[Z-VETO] in Heavy Reasoning: {e}")
            return f"System Hard-Stop: Z-Veto getriggert ({e})"
        except Exception as e:
            logger.error(f"Heavy Reasoning failed: {e}")
            return f"Fehler in Heavy Reasoning: {e}"

# Singleton instance for the app
core_llm = LLMInterface()

# force reload

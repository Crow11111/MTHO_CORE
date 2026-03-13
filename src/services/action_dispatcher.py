# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
CORE: Action Dispatcher
Parses OC Brain responses for autonomous actions (e.g., Home Assistant services).
Format: [HA: domain.service(entity_id, {"key": "value"})]
"""
import re
import json
from loguru import logger
from src.network.ha_client import HAClient

class ActionDispatcher:
    def __init__(self):
        self.ha = HAClient()
        # Regex für: [HA: domain.service(entity_id, {json_data})]
        # Gruppe 1: domain, Gruppe 2: service, Gruppe 3: entity_id, Gruppe 4: json_data
        self.ha_pattern = re.compile(r"\[HA:\s*(\w+)\.(\w+)\(([^,)]+)?(?:,\s*(\{.*?\}))?\s*\)\]")

    def dispatch(self, text: str) -> list[dict]:
        """
        Sucht nach Kommandos im Text und führt sie aus.
        Returns: Liste der ausgeführten Aktionen.
        """
        results = []
        matches = self.ha_pattern.finditer(text)
        
        for match in matches:
            domain = match.group(1)
            service = match.group(2)
            entity_id = match.group(3).strip() if match.group(3) else None
            data_str = match.group(4)
            
            service_data = {}
            if data_str:
                try:
                    service_data = json.loads(data_str)
                except json.JSONDecodeError as e:
                    logger.error("Fehler beim Parsen von HA service_data: {}", e)
                    continue

            logger.info("Führe HA Aktion aus: {}.{} für {}", domain, service, entity_id)
            success = self.ha.call_service(domain, service, entity_id, service_data)
            
            results.append({
                "type": "ha",
                "domain": domain,
                "service": service,
                "entity_id": entity_id,
                "data": service_data,
                "success": success
            })
            
        return results

if __name__ == "__main__":
    # Test
    dispatcher = ActionDispatcher()
    test_text = "Ich werde das Licht einschalten. [HA: light.turn_on(light.living_room, {\"brightness\": 200})] Und die Heizung. [HA: climate.set_temperature(climate.living_room, {\"temperature\": 22})]"
    res = dispatcher.dispatch(test_text)
    print(f"Ausgeführte Aktionen: {res}")

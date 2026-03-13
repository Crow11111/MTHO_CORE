# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import logging
from typing import Dict
from src.config.engine_patterns import INV_PHI, COMP_PHI

logger = logging.getLogger(__name__)

ENTROPY_FOCUS_THRESHOLD = INV_PHI   # 0.618 – Goldener Schnitt (V6)
ENTROPY_SLEEP_THRESHOLD = COMP_PHI  # 0.382 – Komplement (V6)


class AdaptiveSensorScaler:
    """
    Kapselt die Logik für den 'Visuellen Halbschlaf'.
    Sensoren laufen auf absolutem Minimum (z.B. 720p @ 0.5fps) um Hardware-Limits (80/20 Regel) zu respektieren.
    Nur bei Entropie-Druck (Wake-Word, Dissonanz, starke Bewegung) skaliert das System nahtlos hoch.
    """
    def __init__(self):
        self.current_state = "SLEEP" # SLEEP, FOCUS
        self.sensor_configs = {
            "camera_main": {"resolution": "720p", "fps": 0.49},
            "mic_array": {"sample_rate": 16000, "channels": 1}
        }

    def evaluate_entropy(self, entropy_level: float, trigger_event: str = None) -> Dict[str, dict]:
        """
        Wertet die aktuelle Dissonanz oder konkrete Trigger (Wake-Word) aus 
        und gibt die neuen Hardware-Parameter zurück.
        """
        # Wenn Wake-Word fällt oder Dissonanz hoch ist -> Fokus
        if (entropy_level > ENTROPY_FOCUS_THRESHOLD or trigger_event == "wake_word") and self.current_state == "SLEEP":
            logger.info("Fokus benötigt (Entropie hoch / Trigger). Skaliere Sensoren auf FOCUS (4K, 30fps).")
            self.current_state = "FOCUS"
            self.sensor_configs["camera_main"] = {"resolution": "4k", "fps": 30}
            self.sensor_configs["mic_array"] = {"sample_rate": 48000, "channels": 2}
            
        # Wenn System sich beruhigt -> Zurück in Halbschlaf
        elif entropy_level <= ENTROPY_SLEEP_THRESHOLD and not trigger_event and self.current_state == "FOCUS":
            logger.info("System stabil. Skaliere Sensoren auf SLEEP (720p, 0.49fps).")
            self.current_state = "SLEEP"
            self.sensor_configs["camera_main"] = {"resolution": "720p", "fps": 0.49}
            self.sensor_configs["mic_array"] = {"sample_rate": 16000, "channels": 1}
        
        return self.sensor_configs

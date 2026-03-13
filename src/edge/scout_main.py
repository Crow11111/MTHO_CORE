# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import asyncio
import os
import logging
from src.edge.sensor_bus import SensorBus
from src.edge.failover_manager import FailoverManager
from src.edge.adaptive_sensor_scaling import AdaptiveSensorScaler

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("ScoutMain")

async def mock_sensor_loop(failover_mgr: FailoverManager, scaler: AdaptiveSensorScaler):
    """Simuliert Wake-Word Trigger oder MQTT-Events vom HomeAssistant."""
    logger.info("Starte Mock-Sensorschleife auf dem Raspi 5...")
    
    while True:
        await asyncio.sleep(5.0) # Simulierter Sensor-Intervall
        
        # Simuliere dynamischen Entropie-Druck oder Wake-Word
        # In Prod: Reale Audio/Video/MQTT-Daten
        simulated_entropy = 0.1
        trigger = None
        
        import random
        if random.random() > 0.8:
            simulated_entropy = 0.8
            trigger = "wake_word"
            logger.info(">> WAKE-WORD DETEKTIERT <<")

        # Passe Hardware-Ressourcen an (Halbschlaf vs Fokus)
        current_config = scaler.evaluate_entropy(simulated_entropy, trigger)
        
        # Sende Daten an den Bus
        payload = {
            "type": "audio_frame",
            "entropy": simulated_entropy,
            "config": current_config
        }
        
        await failover_mgr.route_event("raspi_mic_01", payload)

async def main():
    vps_endpoint = os.environ.get("VPS_ENDPOINT", "http://127.0.0.1:8000/api/sensor")
    vps_ping_url = os.environ.get("VPS_PING_URL", "http://127.0.0.1:8000/health")
    dreadnought_ping_url = os.environ.get("DREADNOUGHT_PING_URL", "http://127.0.0.1:8001/health")

    logger.info(f"Initialisiere Scout. VPS: {vps_endpoint}")

    sensor_bus = SensorBus(vps_endpoint=vps_endpoint)
    failover_mgr = FailoverManager(vps_ping_url, dreadnought_ping_url, sensor_bus)
    scaler = AdaptiveSensorScaler()

    await sensor_bus.start()
    await failover_mgr.start()

    try:
        await mock_sensor_loop(failover_mgr, scaler)
    except asyncio.CancelledError:
        logger.info("Scout wird beendet...")
    finally:
        await failover_mgr.stop()
        await sensor_bus.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")

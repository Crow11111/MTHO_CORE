# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

import logging
from fastapi import FastAPI
from dotenv import load_dotenv

# Env laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Router importieren
from src.api.whatsapp_bridge import router as whatsapp_router

app = FastAPI(
    title="CORE AGI Core",
    description="Einstiegspunkt für WhatsApp Bridge und Sensor Bus",
    version="1.0.0"
)

# Router mounten
app.include_router(whatsapp_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "agi-core"}

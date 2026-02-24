from fastapi import FastAPI
from src.api.routes import whatsapp_webhook, ha_webhook
import os

app = FastAPI(
    title="ATLAS_CORE API",
    description="Main Backend Interface for ATLAS Operations",
    version="1.0.0"
)

# Registrierung der Routen (Webhooks)
app.include_router(whatsapp_webhook.router)
app.include_router(ha_webhook.router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "ATLAS_CORE", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    # Local Test Runner
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)

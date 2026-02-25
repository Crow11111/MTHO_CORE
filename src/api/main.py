import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import whatsapp_webhook, ha_webhook, dev_agent_ws

app = FastAPI(
    title="ATLAS_CORE API",
    description="Main Backend Interface for ATLAS Operations",
    version="1.0.0"
)

# CORS für Dev-Agent-Frontend (z. B. localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrierung der Routen (Webhooks + Dev-Agent WS/REST)
app.include_router(whatsapp_webhook.router)
app.include_router(ha_webhook.router)
app.include_router(dev_agent_ws.router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "ATLAS_CORE", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    # Local Test Runner
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)

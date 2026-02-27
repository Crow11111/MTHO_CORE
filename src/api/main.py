import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import whatsapp_webhook, ha_webhook, oc_channel

app = FastAPI(
    title="ATLAS_CORE API",
    description="Main Backend Interface for ATLAS Operations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrierung der Routen (Webhooks + OpenClaw Channel)
app.include_router(whatsapp_webhook.router)
app.include_router(ha_webhook.router)
app.include_router(oc_channel.router)

@app.get("/")
def read_root():
    return {"status": "online", "system": "ATLAS_CORE", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    # Test-Aufruf lokal (z.B. python -m src.api.main)
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
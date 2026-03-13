from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from src.logic_core.id_safe import id_safe_instance, IdentityDocument

router = APIRouter(prefix="/api/core", tags=["identity"])

# Dummy-Auth fuer lokale Entwicklung
async def get_current_user():
    # In einer echten Anwendung wuerde hier die Authentifizierung erfolgen
    # Fuer diese Demo nehmen wir an, der User ist immer authentifiziert
    return {"username": "system_user"}


@router.post("/id_safe/document", response_model=IdentityDocument)
async def add_identity_document(doc: IdentityDocument, current_user: dict = Depends(get_current_user)):
    """Fuegt ein Identitätsdokument hinzu oder aktualisiert es im IDSafe."""
    try:
        await id_safe_instance.add_document(doc)
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hinzufügen des Dokuments: {e}")

@router.get("/id_safe/document/{doc_id}", response_model=IdentityDocument)
async def get_identity_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Ruft ein Identitätsdokument anhand seiner ID ab."""
    try:
        doc = await id_safe_instance.get_document(doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Dokuments: {e}")

@router.post("/id_safe/search", response_model=List[IdentityDocument])
async def search_identity_documents(query: str, limit: int = 5, current_user: dict = Depends(get_current_user)):
    """Durchsucht Identitätsdokumente nach relevanten Informationen."""
    try:
        results = await id_safe_instance.search_documents(query, limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Dokumentsuche: {e}")

@router.get("/id_safe/status", response_model=Dict[str, List[IdentityDocument]])
async def get_document_status(current_user: dict = Depends(get_current_user)):
    """Gibt den Status aller Dokumente zurück und warnt vor abgelaufenen oder bald ablaufenden."""
    try:
        all_docs = await id_safe_instance.search_documents(query="", limit=100) # Alle Dokumente abrufen
        expired_docs = []
        expiring_soon_docs = [] # Z.B. innerhalb der nächsten 3 Monate
        lost_docs = []

        for doc in all_docs:
            if doc.status == "lost" or doc.status == "stolen":
                lost_docs.append(doc)
            elif doc.expiry_date and doc.expiry_date < datetime.now():
                expired_docs.append(doc)
            elif doc.expiry_date and (doc.expiry_date - datetime.now()).days < 90:
                expiring_soon_docs.append(doc)

        return {
            "lost": lost_docs,
            "expired": expired_docs,
            "expiring_soon": expiring_soon_docs,
            "active": [d for d in all_docs if d.status == "active"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Dokumentstatus: {e}")

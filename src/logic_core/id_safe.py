import os
import json
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from src.network.chroma_client import ChromaClient
from loguru import logger

class IdentityDocument(BaseModel):
    """Repräsentiert ein digitales Identitätsdokument."""
    id: str = Field(..., description="Eindeutige ID des Dokuments (z.B. Ausweisnummer, Geburtsdatum-Typ)")
    document_type: str = Field(..., description="Art des Dokuments (z.B. 'Personalausweis', 'Geburtsurkunde', 'Führerschein', 'Wohnungsgeberbestätigung')")
    name: str = Field(..., description="Name des Dokumenteninhabers")
    issue_date: Optional[datetime] = Field(None, description="Ausstellungsdatum des Dokuments")
    expiry_date: Optional[datetime] = Field(None, description="Ablaufdatum des Dokuments")
    status: str = Field("active", description="Aktueller Status des Dokuments ('active', 'expired', 'lost', 'stolen', 'replaced')")
    content_summary: str = Field(..., description="Kurze Zusammenfassung des Inhalts oder Referenz auf den physischen Ort/Scan")
    tags: List[str] = Field([], description="Zusätzliche Tags zur Kategorisierung")
    source_context: Optional[str] = Field(None, description="Kontext, woher das Dokument stammt (z.B. 'Scan vom Bürgeramt 2023')")

    def to_document(self) -> Dict:
        """Konvertiert das Modell in ein ChromaDB-Dokumentformat."""
        return {
            "id": self.id,
            "document": self.content_summary,
            "metadata": self.model_dump(exclude={"id", "content_summary"})
        }

class IDSafe:
    """Verwaltet digitale Identitätsdokumente in ChromaDB."""
    def __init__(self):
        self.client = ChromaClient()
        self.collection_name = "core_identity_documents"
        self._ensure_collection()

    def _ensure_collection(self):
        """Stellt sicher, dass die ChromaDB Collection existiert."""
        try:
            self.client.get_or_create_collection(self.collection_name)
            logger.info(f"[IDSafe] Collection '{self.collection_name}' ist bereit.")
        except Exception as e:
            logger.error(f"[IDSafe] Fehler beim Initialisieren der Collection '{self.collection_name}': {e}")
            raise

    async def add_document(self, doc: IdentityDocument):
        """Fügt ein Identitätsdokument hinzu oder aktualisiert es."""
        try:
            await self.client.upsert_documents(
                collection_name=self.collection_name,
                documents=[doc.to_document()]
            )
            logger.info(f"[IDSafe] Dokument '{doc.id}' vom Typ '{doc.document_type}' hinzugefügt/aktualisiert.")
        except Exception as e:
            logger.error(f"[IDSafe] Fehler beim Hinzufügen/Aktualisieren von Dokument '{doc.id}': {e}")
            raise

    async def get_document(self, doc_id: str) -> Optional[IdentityDocument]:
        """Ruft ein Identitätsdokument anhand seiner ID ab."""
        try:
            results = await self.client.get_documents(
                collection_name=self.collection_name,
                ids=[doc_id]
            )
            if results and results.get("documents"):
                doc_data = results["documents"][0]
                metadata = results["metadatas"][0]
                # Kombiniere doc_data und metadata, um das Pydantic-Modell zu erstellen
                full_data = {
                    "id": doc_id,
                    "content_summary": doc_data,
                    **metadata
                }
                return IdentityDocument(**full_data)
            return None
        except Exception as e:
            logger.error(f"[IDSafe] Fehler beim Abrufen von Dokument '{doc_id}': {e}")
            raise

    async def search_documents(self, query: str, limit: int = 5) -> List[IdentityDocument]:
        """Durchsucht Dokumente nach relevanten Informationen."""
        try:
            results = await self.client.query_documents(
                collection_name=self.collection_name,
                query_texts=[query],
                n_results=limit
            )
            found_docs = []
            if results and results.get("documents"):
                for i, doc_data in enumerate(results["documents"]):
                    metadata = results["metadatas"][i]
                    doc_id = results["ids"][i]
                    full_data = {
                        "id": doc_id,
                        "content_summary": doc_data,
                        **metadata
                    }
                    found_docs.append(IdentityDocument(**full_data))
            return found_docs
        except Exception as e:
            logger.error(f"[IDSafe] Fehler bei der Dokumentsuche mit Query '{query}': {e}")
            raise

id_safe_instance = IDSafe()

# Beispiel der Nutzung (kann entfernt oder in Tests verschoben werden)
async def main():
    doc1 = IdentityDocument(
        id="PASSPORT-12345",
        document_type="Reisepass",
        name="Marc Tobias ten Hoevel",
        issue_date=datetime(2020, 1, 15),
        expiry_date=datetime(2030, 1, 15),
        status="active",
        content_summary="Digitaler Scan des aktuellen Reisepasses",
        tags=["Reise", "Identifikation"]
    )

    await id_safe_instance.add_document(doc1)

    found_doc = await id_safe_instance.get_document("PASSPORT-12345")
    if found_doc:
        print(f"Gefundenes Dokument: {found_doc.name}, Typ: {found_doc.document_type}")

    search_results = await id_safe_instance.search_documents("Ausweis von Marc")
    if search_results:
        print(f"Suchergebnisse: {[d.document_type for d in search_results]}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

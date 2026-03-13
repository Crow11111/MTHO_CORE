# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
AUFGABE 1: Dokument ntnd_handshake_protocol zu lokaler core_directives hinzufügen.
AUFGABE 2: Dasselbe Dokument per REST API an VPS ChromaDB spiegeln.
"""
import os
import sys
import urllib3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import chromadb
import requests

# Konfiguration
LOCAL_PATH = r"c:\CORE\data\chroma_db"
VPS_BASE = "https://187.77.68.250/chroma/api/v2"
VERIFY_SSL = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TENANT = "default_tenant"
DATABASE = "default_database"

DOCUMENT = """NT/ND CONS-ZELLEN-PROTOKOLL (Binäre Symmetrie-Logik)

Jede Zelle im CORE-System ist ein Binär-Paar (Lisp cons-cell):
- CAR (ND-Kern): Tiefe, monotropistischer Fokus, Mustererkennung, divergentes Denken, antike Matrix.
- CDR (NT-Interface): Mapping, Dokumentation, API-Syntax, Clean Code, Cursor-Kompatibilität, operative Realität.

REGEL: Jeder Agent-Output MUSS eine NT-kompatible Hülle (CDR) besitzen, die den ND-Kern (CAR) für den nächsten Takt konsumierbar macht.

Cons-Zellen pro Strang:
- ExecutionRuntime (Macher): CAR=Effizienz-Hacks, CDR=Clean Code/PEP8/Tests
- ConstraintValidator (Richter): CAR=Paranoia/Anomalie-Erkennung, CDR=Compliance/JSON-Veto
- LogicFlow (Träumer): CAR=Chaos/Was-wäre-wenn, CDR=Architektur-Spec/Constraint-Schema
- StateAnchor (Bewahrer): CAR=Assoziative Vektor-Cluster, CDR=SQL-Index/API-Responses

Handshake: Kommunikation zwischen Strängen läuft IMMER über CDR (NT-Interface). CAR bleibt intern."""

METADATA = {"type": "protocol", "priority": "ring-0", "source": "agos_phase_shift_v2", "date": "2026-03-02"}
ID_ = "ntnd_handshake_protocol"


def task1_local() -> int:
    """AUFGABE 1: Lokale ChromaDB."""
    client = chromadb.PersistentClient(path=LOCAL_PATH)
    col = client.get_collection("core_directives")
    col.add(
        ids=[ID_],
        documents=[DOCUMENT],
        metadatas=[METADATA],
    )
    count = col.count()
    print(f"[Lokal] core_directives count: {count}")
    return count


def _sanitize_metadata(m):
    """ChromaDB erlaubt nur str, int, float, bool."""
    if m is None:
        return None
    out = {}
    for k, v in m.items():
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        elif v is None:
            out[k] = ""
        else:
            out[k] = str(v)
    return out


def task2_vps() -> int | None:
    """AUFGABE 2: VPS ChromaDB per REST API."""
    base = VPS_BASE.rstrip("/")

    # Collection holen oder erstellen
    url_create = f"{base}/tenants/{TENANT}/databases/{DATABASE}/collections"
    r = requests.post(
        url_create,
        json={"name": "core_directives", "get_or_create": True},
        timeout=30,
        verify=VERIFY_SSL,
    )
    r.raise_for_status()
    coll_id = r.json().get("id")
    if not coll_id:
        print("[VPS] Collection-ID nicht erhalten")
        return None

    # Record aus lokaler DB lesen (mit Embeddings)
    client = chromadb.PersistentClient(path=LOCAL_PATH)
    col = client.get_collection("core_directives")
    data = col.get(ids=[ID_], include=["documents", "embeddings", "metadatas"])
    if not data["ids"]:
        print("[VPS] Record ntnd_handshake_protocol lokal nicht gefunden")
        return None

    embeddings = data.get("embeddings")
    if embeddings is not None and len(embeddings) > 0:
        emb = embeddings[0]
        vec = emb.tolist() if hasattr(emb, "tolist") else list(emb)
        emb_list = [vec]
    else:
        emb_list = [[0.0] * 384]  # Fallback

    # Add per REST
    url_add = f"{base}/tenants/{TENANT}/databases/{DATABASE}/collections/{coll_id}/add"
    payload = {
        "ids": [ID_],
        "embeddings": emb_list,
        "documents": [DOCUMENT],
        "metadatas": [_sanitize_metadata(METADATA)],
    }
    r2 = requests.post(url_add, json=payload, timeout=60, verify=VERIFY_SSL)
    r2.raise_for_status()

    # Count holen
    url_count = f"{base}/tenants/{TENANT}/databases/{DATABASE}/collections/{coll_id}/count"
    r3 = requests.get(url_count, timeout=10, verify=VERIFY_SSL)
    r3.raise_for_status()
    count = int(r3.json()) if r3.text else None
    print(f"[VPS] core_directives count: {count}")
    return count


def main():
    print("=== AUFGABE 1: Lokale ChromaDB ===")
    local_count = task1_local()

    print("\n=== AUFGABE 2: VPS ChromaDB ===")
    try:
        vps_count = task2_vps()
    except Exception as e:
        print(f"[VPS] Fehler: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(e.response.text[:500])
        vps_count = None

    print("\n--- Ergebnis ---")
    print(f"Lokal core_directives: {local_count}")
    print(f"VPS core_directives:   {vps_count}")


if __name__ == "__main__":
    main()

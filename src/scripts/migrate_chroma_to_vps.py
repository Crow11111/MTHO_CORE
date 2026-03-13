# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
ChromaDB Migration: Dreadnought (lokal) -> VPS.
Liest simulation_evidence, session_logs, core_directives aus lokalem chroma_db,
schreibt via ChromaDB v2 REST API auf VPS.
"""
import os
import sys
import urllib3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests

# Konfiguration
LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\CORE\data\chroma_db")
VPS_BASE = os.getenv("CHROMA_VPS_URL", "https://187.77.68.250/chroma/api/v2")
# VPS oft mit self-signed cert; CHROMA_SSL_VERIFY=true für Verifikation
VERIFY_SSL = os.getenv("CHROMA_SSL_VERIFY", "false").lower() in ("1", "true", "yes")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TENANT = "default_tenant"
DATABASE = "default_database"
COLLECTIONS = ["simulation_evidence", "session_logs", "core_directives"]
BATCH_SIZE = 50


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


def read_local_collection(name: str) -> dict | None:
    """Liest Collection aus lokalem PersistentClient."""
    try:
        import chromadb
    except ImportError:
        print("chromadb nicht installiert: pip install chromadb")
        return None
    if not os.path.exists(LOCAL_PATH):
        print(f"Lokaler Pfad existiert nicht: {LOCAL_PATH}")
        return None
    client = chromadb.PersistentClient(path=LOCAL_PATH)
    try:
        coll = client.get_collection(name=name)
    except Exception as e:
        print(f"Collection {name} nicht gefunden: {e}")
        return None
    data = coll.get(include=["documents", "embeddings", "metadatas"])
    return data


def create_or_get_collection(base_url: str, name: str) -> str | None:
    """Erstellt Collection auf VPS (get_or_create). Gibt collection_id (UUID) zurück."""
    url = f"{base_url}/tenants/{TENANT}/databases/{DATABASE}/collections"
    payload = {"name": name, "get_or_create": True}
    try:
        r = requests.post(url, json=payload, timeout=30, verify=VERIFY_SSL)
        r.raise_for_status()
        body = r.json()
        return body.get("id")
    except Exception as e:
        print(f"Create collection {name} fehlgeschlagen: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(e.response.text[:500])
        return None


def add_records(base_url: str, collection_id: str, ids: list, embeddings: list, documents: list | None, metadatas: list | None) -> bool:
    """Fügt Records zur Collection hinzu."""
    url = f"{base_url}/tenants/{TENANT}/databases/{DATABASE}/collections/{collection_id}/add"
    payload = {"ids": ids, "embeddings": embeddings}
    if documents:
        payload["documents"] = documents
    if metadatas:
        payload["metadatas"] = [_sanitize_metadata(m) for m in metadatas]
    try:
        r = requests.post(url, json=payload, timeout=60, verify=VERIFY_SSL)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"Add records fehlgeschlagen: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(e.response.text[:500])
        return False


def migrate_collection(base_url: str, name: str) -> int:
    """Migriert eine Collection. Gibt Anzahl migrierter Records zurück."""
    data = read_local_collection(name)
    if not data or not data.get("ids"):
        print(f"[{name}] Keine Daten oder leer.")
        return 0
    ids = data["ids"]
    embeddings = data.get("embeddings")
    documents = data.get("documents")
    metadatas = data.get("metadatas")
    if embeddings is None or (hasattr(embeddings, "__len__") and len(embeddings) == 0):
        # Fallback: Null-Embedding wenn Collection ohne Embedding (z.B. metadata-only)
        dim = 384  # ChromaDB Default
        embeddings = [[0.0] * dim] * len(ids)
    else:
        # numpy -> list (JSON-serialisierbar)
        embeddings = [e.tolist() if hasattr(e, "tolist") else list(e) for e in embeddings]
    if not documents:
        documents = [""] * len(ids)
    if not metadatas:
        metadatas = [None] * len(ids)
    coll_id = create_or_get_collection(base_url, name)
    if not coll_id:
        return 0
    migrated = 0
    for i in range(0, len(ids), BATCH_SIZE):
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_emb = embeddings[i : i + BATCH_SIZE]
        batch_doc = documents[i : i + BATCH_SIZE]
        batch_meta = metadatas[i : i + BATCH_SIZE]
        if add_records(base_url, coll_id, batch_ids, batch_emb, batch_doc, batch_meta):
            migrated += len(batch_ids)
            print(f"  Batch {i // BATCH_SIZE + 1}: {len(batch_ids)} Records")
        else:
            break
    return migrated


def get_collection_count(base_url: str, collection_id: str) -> int | None:
    """Holt Record-Count einer Collection via GET .../count."""
    url = f"{base_url}/tenants/{TENANT}/databases/{DATABASE}/collections/{collection_id}/count"
    try:
        r = requests.get(url, timeout=10, verify=VERIFY_SSL)
        r.raise_for_status()
        return int(r.json()) if r.text else None
    except Exception:
        return None


def verify_vps(base_url: str) -> dict:
    """Prüft Collections und Counts auf VPS via GET (falls API unterstützt)."""
    url = f"{base_url}/tenants/{TENANT}/databases/{DATABASE}/collections"
    try:
        r = requests.get(url, timeout=15, verify=VERIFY_SSL)
        r.raise_for_status()
        colls = r.json()
        if isinstance(colls, list):
            return {c.get("name", "?"): c for c in colls}
        return {}
    except Exception as e:
        print(f"Verify (GET collections) fehlgeschlagen: {e}")
        return {}


def main():
    base = VPS_BASE.rstrip("/")
    print(f"Migration: {LOCAL_PATH} -> {base}")
    print("-" * 50)
    total = 0
    for name in COLLECTIONS:
        print(f"\n[{name}]")
        n = migrate_collection(base, name)
        total += n
        print(f"  -> {n} Records migriert")
    print("-" * 50)
    print(f"Gesamt: {total} Records")
    print("\nVerifikation (VPS Collections):")
    info = verify_vps(base)
    for name in COLLECTIONS:
        c = info.get(name, {})
        cid = c.get("id")
        cnt = get_collection_count(base, cid) if cid else None
        cnt_str = str(cnt) if cnt is not None else "?"
        print(f"  {name}: {cid or '?'} | Count: {cnt_str}")
    if not info:
        print("  (GET collections nicht verfügbar - manuell prüfen)")


if __name__ == "__main__":
    main()

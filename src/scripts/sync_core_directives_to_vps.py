# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

#!/usr/bin/env python3
"""
Synchronisiert alle core_directives von lokaler ChromaDB zum VPS.
Voraussetzung: SSH-Tunnel zur VPS-ChromaDB (z. B. ssh -L 8000:127.0.0.1:8000 root@187.77.68.250).
Umgebung: CHROMA_VPS_HOST=localhost CHROMA_VPS_PORT=8000 (oder Standard localhost:8000).
Lokale DB: CHROMA_LOCAL_PATH bzw. c:\\CORE\\data\\chroma_db.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\CORE\data\chroma_db")
VPS_HOST = os.getenv("CHROMA_VPS_HOST", "localhost")
VPS_PORT = int(os.getenv("CHROMA_VPS_PORT", "8000"))


def _sanitize_meta(m):
    if m is None:
        return {}
    return {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()}


def main():
    import chromadb

    # 1) Lokal lesen
    client_local = chromadb.PersistentClient(path=LOCAL_PATH)
    col_local = client_local.get_collection("core_directives")
    n_local = col_local.count()
    if n_local == 0:
        print("Lokal: 0 core_directives. Nichts zu syncen.")
        return
    data = col_local.get(include=["documents", "metadatas"])
    ids = data["ids"]
    documents = data["documents"]
    metadatas = data.get("metadatas") or [{}] * len(ids)
    metadatas = [_sanitize_meta(m) for m in metadatas]
    print(f"Lokal: {n_local} Einträge gelesen.")

    # 2) VPS schreiben (HttpClient)
    client_vps = chromadb.HttpClient(host=VPS_HOST, port=VPS_PORT)
    col_vps = client_vps.get_or_create_collection("core_directives", metadata={"description": "CORE core_directives"})
    col_vps.upsert(ids=ids, documents=documents, metadatas=metadatas)
    n_vps = col_vps.count()
    print(f"VPS ({VPS_HOST}:{VPS_PORT}): {n_vps} Einträge nach Sync.")
    print("Sync abgeschlossen. Tunnel ggf. beenden.")


if __name__ == "__main__":
    main()

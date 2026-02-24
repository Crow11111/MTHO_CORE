import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Osmium Council: Low Latency Database Settings (WAL-Mode)
DB_PATH = r"c:\ATLAS_CORE\data\argos_db\argos_knowledge_graph.sqlite"

app = FastAPI(title="ATLAS_CORE Database Backend (Osmium Standard V1.3)")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    # --- Original Osmium Tables ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS core_brain_registr (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
            system_status TEXT CHECK(system_status IN ('active', 'inactive')),
            content TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS krypto_scan_buffer (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            threat_level TEXT CHECK(threat_level IN ('low', 'medium', 'high')),
            affected_resources TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS argos_knowledge_graph (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component1 TEXT,
            component2 TEXT,
            relation_type TEXT CHECK(relation_type IN ('influence', 'causality')),
            source_file TEXT
        )
    """)
    
    # --- Phase 7: Osmium Circle V1.3 Tables ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS osmium_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            layer TEXT NOT NULL CHECK(layer IN ('operative', 'council')),
            function TEXT NOT NULL,
            voice_design TEXT,
            voice_id TEXT DEFAULT '',
            stability REAL DEFAULT 0.75,
            similarity REAL DEFAULT 0.80,
            style REAL DEFAULT 0.0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS emotional_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_prefix TEXT UNIQUE NOT NULL,
            trigger_context TEXT NOT NULL,
            audio_signature TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS proactive_triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vector_name TEXT UNIQUE NOT NULL,
            condition TEXT NOT NULL,
            target_role TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_role) REFERENCES osmium_roles(name)
        )
    """)
    conn.commit()
    return conn

# --- Pydantic Models (ATLAS Data Atoms) ---
class CoreBrainRegistr(BaseModel):
    system_status: str
    content: str

class KryptoScanBuffer(BaseModel):
    threat_level: str
    affected_resources: str

class ArgosKnowledgeGraph(BaseModel):
    component1: str
    component2: str
    relation_type: str
    source_file: Optional[str] = None

class OsmiumRole(BaseModel):
    name: str
    layer: str
    function: str
    voice_design: Optional[str] = None
    voice_id: Optional[str] = ""
    stability: Optional[float] = 0.75
    similarity: Optional[float] = 0.80
    style: Optional[float] = 0.0

class EmotionalState(BaseModel):
    state_prefix: str
    trigger_context: str
    audio_signature: str

class ProactiveTrigger(BaseModel):
    vector_name: str
    condition: str
    target_role: str

# --- API Endpoints ---
@app.on_event("startup")
def startup():
    get_db_connection().close()

# --- Core Brain ---
@app.get("/core_brain", response_model=List[dict])
def get_core_brain():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM core_brain_registr").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/core_brain")
def add_core_brain(entry: CoreBrainRegistr):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO core_brain_registr (system_status, content) VALUES (?, ?)", (entry.system_status, entry.content))
    conn.commit()
    conn.close()
    return {"status": "success", "id": cursor.lastrowid}

# --- Knowledge Graph ---
@app.get("/knowledge_graph", response_model=List[dict])
def get_knowledge_graph():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM argos_knowledge_graph").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/knowledge_graph")
def add_knowledge_graph(entry: ArgosKnowledgeGraph):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO argos_knowledge_graph (component1, component2, relation_type, source_file) VALUES (?, ?, ?, ?)", 
                   (entry.component1, entry.component2, entry.relation_type, entry.source_file))
    conn.commit()
    conn.close()
    return {"status": "success", "id": cursor.lastrowid}

# --- Krypto Scan ---
@app.get("/krypto_scan", response_model=List[dict])
def get_krypto_scan():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM krypto_scan_buffer").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/krypto_scan")
def add_krypto_scan(entry: KryptoScanBuffer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO krypto_scan_buffer (threat_level, affected_resources) VALUES (?, ?)", 
                   (entry.threat_level, entry.affected_resources))
    conn.commit()
    conn.close()
    return {"status": "success", "id": cursor.lastrowid}

# --- Osmium Roles (Phase 7) ---
@app.get("/osmium_roles", response_model=List[dict])
def get_osmium_roles(name: Optional[str] = Query(None), layer: Optional[str] = Query(None)):
    conn = get_db_connection()
    query = "SELECT * FROM osmium_roles WHERE 1=1"
    params = []
    if name:
        query += " AND name = ?"
        params.append(name)
    if layer:
        query += " AND layer = ?"
        params.append(layer)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/osmium_roles")
def add_osmium_role(entry: OsmiumRole):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO osmium_roles (name, layer, function, voice_design, voice_id, stability, similarity, style) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (entry.name, entry.layer, entry.function, entry.voice_design, entry.voice_id, entry.stability, entry.similarity, entry.style))
        conn.commit()
        return {"status": "success", "id": cursor.lastrowid}
    finally:
        conn.close()

# --- Emotional States (Phase 7) ---
@app.get("/emotional_states", response_model=List[dict])
def get_emotional_states():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM emotional_states").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/emotional_states")
def add_emotional_state(entry: EmotionalState):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO emotional_states (state_prefix, trigger_context, audio_signature) VALUES (?, ?, ?)",
            (entry.state_prefix, entry.trigger_context, entry.audio_signature))
        conn.commit()
        return {"status": "success", "id": cursor.lastrowid}
    finally:
        conn.close()

# --- Proactive Triggers (Phase 7) ---
@app.get("/proactive_triggers", response_model=List[dict])
def get_proactive_triggers():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM proactive_triggers").fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/proactive_triggers")
def add_proactive_trigger(entry: ProactiveTrigger):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO proactive_triggers (vector_name, condition, target_role) VALUES (?, ?, ?)",
            (entry.vector_name, entry.condition, entry.target_role))
        conn.commit()
        return {"status": "success", "id": cursor.lastrowid}
    finally:
        conn.close()

if __name__ == "__main__":
    import uvicorn
    print("[ATLAS_CORE] Starting Osmium Database Backend V1.3 (Port 8000)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

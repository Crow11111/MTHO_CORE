#!/usr/bin/env python3
"""Indiziert den Nano Banana Pro Master-Prompt in ChromaDB."""

import chromadb
from datetime import datetime

client = chromadb.PersistentClient(path=r"c:\CORE\data\chroma_db")
col = client.get_or_create_collection("core_directives")

doc_id = "nano_banana_tesserakt_master_prompt_v1"

document = """# Master-Prompt für Nano Banana Pro (Tesserakt-Architektur)

Create a hyper-realistic, maximum resolution technical architectural visualization of the "CORE-GENESIS" system, designed strictly as a glowing TESSERACT (a 4D hypercube projected into a 3D shadow box). Visual style: Nano Banana Pro aesthetic, futuristic neon cyan, gold, and deep magenta glowing circuitry on a pitch-black, professional carbon-fiber blueprint background.

## GEOMETRY & PLACEMENT:

### 1. THE INNER CUBE (The Singularity)
Deep in the center, a highly condensed, glowing core.
- Label: "OMEGA_ATTRACTOR (Vektor 0 / OpenClaw)"
- Add a holographic brain/crown icon.
- Add text: "Zero-State-Veto (0)" floating perfectly inside this inner cube.

### 2. THE OUTER CUBE (The Physical Shell)
The large, transparent structural box enclosing the inner core.
- Top outer face: "ChromaDB (StateAnchor) / simulation_evidence"
- Right outer face: "VPS-Slim (:8001)"
- Bottom outer face: "Scout (Home Assistant)"
- Left outer face: "4D_RESONATOR (CORE)"

### 3. THE DIAGONAL STRUTS (The Data Verschränkung)
The glowing beams connecting the corners of the inner cube to the outer cube.
- Front-left strut: "Takt 0 (Diagnose)" (glowing security gate)
- Bottom strut: "Gravitator (Semantic Routing)" (glowing prism)
- Left strut: "Entry Adapter" (filter node)
- Right strut: "CRADLE (:8049)" (relay node)

## DATA CHANNELS & AXIOMS:
- Draw intense beams of light traveling simultaneously IN BOTH DIRECTIONS along the struts, labeled "/inject" and "/vectors".
- Top left corner axioms: "VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049 | LOGIC: 2-2-1-0 (SIMULTANEOUS)"
- Bottom right: fortified shield icon labeled "Code-Sicherheitsrat"

## AESTHETICS:
Rendered in Unreal Engine 5 style, extreme macro detailing, glass dispersion, volumetric lighting, ensuring the geometric relationship between the inner core and outer shell perfectly illustrates a 4D tesseract shadow.

---
Source: Gemini Share 5c17c6dbd7e2
"""

document += f"Indexed: {datetime.now().isoformat()}"

metadata = {
    "type": "master_prompt",
    "category": "visualization",
    "tool": "nano_banana_pro",
    "geometry": "tesserakt_4d",
    "source": "gemini_share_5c17c6dbd7e2",
    "indexed_at": datetime.now().isoformat(),
    "vector": "2210",
    "resonance": "0221",
    "delta": "0.049",
}

col.upsert(ids=[doc_id], documents=[document], metadatas=[metadata])
print(f"Indiziert: {doc_id}")
print(f"Collection count: {col.count()}")

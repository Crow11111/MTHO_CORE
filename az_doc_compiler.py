import os
import time
from typing import Dict, List, Optional

import ollama
from dotenv import load_dotenv
from loguru import logger

# ==========================================
# CONFIGURATION: PLANCK_CORE
# ==========================================
# Load environment variables from .env file
load_dotenv()

DOCS_OUTPUT_DIR = os.getenv("DATA_PATH", "./data") + "/antigravity_docs_compiled"
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Set Ollama host if provided
if OLLAMA_HOST:
    os.environ["OLLAMA_HOST"] = OLLAMA_HOST

SIGMA_TARGET = 1.99999

# Taxonomy of the Requirement Specification (Atomized)
DOCUMENT_TAXONOMY: Dict[str, List[str]] = {
    "01_ARCHITEKTUR_HARDWARE": [
        "Spezifikation Node Alpha: Windows Host Härtung, Deaktivierung Telemetrie, I/O Optimierung mittels Registry-Tweaks (Service-Härtung).",
        "Spezifikation Node Alpha: WSL2 Ressourcen-Limitierung (.wslconfig) zur Verhinderung von vmmem-Speicherlecks und CPU-Priorisierung.",
        "Spezifikation Node Beta: RPi 5 Edge-Computing, Thermal-Throttling Prävention (Active Cooling PWM Setup), Stromversorgung via PoE-Hat."
    ],
    "02_NETZWERK_SECURITY": [
        "VLAN Topologie (802.1Q) und mTLS Zertifikats-Kette (Internal CA) zwischen Alpha und Beta.",
        "Zero-Trust Policy, SSH-Tunneling (ed25519 Keys) und Port-Sperren auf Host-Ebene mittels Windows Firewall / IPTables."
    ],
    "03_DATENBANK_VECTOR_STORE": [
        "ChromaDB Architektur: Verhinderung von SQLite-Locking durch asynchrone I/O Layer und WAL-Mode (Write-Ahead Logging).",
        "Collection-Layout: core_brain_registr (immutable), krypto_scan_buffer, argos_knowledge_graph.",
        "Backup-Strategie und Disaster-Recovery: Point-in-Time Recovery für Vektor-Embeddings und Metadaten."
    ],
    "04_LOGIC_CORE_AER": [
        "Agnostic Entropy Router (AER): Algorithmus zur Shannon-Entropie Berechnung für dynamisches Aufgaben-Routing.",
        "Routing-Metriken: Latenz-Grenzwerte (p99) für Fallback von Cloud-API auf lokale Modelle (Ollama).",
        "Token Implosion Engine (TIE): Regex-Bereinigung, Deduplizierung und Kompressions-Ratio Analyse."
    ],
    "05_BIAS_DAMPER_ENGINE": [
        "P-Delta Filterlogik: Mathematische Berechnung der kognitiven Dissonanz in LLM-Outputs.",
        "Interventions-Kaskade: Hard-Reject (Gatekeeping) vs. Soft-Flagging (Context-Injection).",
        "ATLAS-JSON Daten-Atom Spezifikation: Schema-Validierung für deterministische KI-Antworten."
    ],
    "06_ARGOS_SYMBIOSIS": [
        "KRYPTO-SCAN Harvester: Asynchrone Python-Queue (asyncio.Queue) für Edge-Scraping und Real-Time Processing.",
        "gRPC API Definitionen (.proto) für Low-Latency Inter-Node Communication.",
        "Integration in bestehende Unternehmens-Infrastruktur: NT-Mapping und Active Directory Bindings."
    ]
}


class DocCompiler:
    """
    Compiler Engine for generating technical documentation using LLMs.
    Adheres to the ARCHITECT_ZERO directive for high-technical specification.
    """

    def __init__(self):
        """Initializes the compiler, ensures output directories exist, and configures logging."""
        if not os.path.exists(DOCS_OUTPUT_DIR):
            os.makedirs(DOCS_OUTPUT_DIR)
        
        logger.add("logs/compiler_{time}.log", rotation="10 MB", level="INFO")
        logger.info("[ATLAS]: Compiler Engine geladen. 5-Sigma Audit aktiv.")
        logger.debug(f"Config: Model={MODEL_NAME}, Output={DOCS_OUTPUT_DIR}")

    def _generate_section(self, section_title: str, prompt_directive: str) -> str:
        """
        Uses the Ollama library to expand atomized points into deep specifications.
        
        Args:
            section_title: The title of the section to generate.
            prompt_directive: The technical focus/points for the section.
            
        Returns:
            The generated technical specification text.
        """
        system_prompt = (
            "Du bist ARCHITEKT ZERO. Schreibe ein unabstrahiertes, hochtechnisches Lastenheft-Kapitel. "
            "Level: IT-Enterprise-Architektur, Datenbank-Design, Systemprogrammierung. "
            "Regeln: Keine Füllwörter, keine Begrüßungen, reine Fakten. Verwende Codelisten, "
            "Hardware-Spezifikationen und mathematische Formeln wo nötig. "
            "Das Zielpublikum hat Expertenwissen in Windows-Systemarchitektur und verteilten Systemen."
        )
        
        full_prompt = f"Generiere das Kapitel: {section_title}\n\nFokus:\n{prompt_directive}"
        
        for attempt in range(3):
            try:
                logger.info(f"[ATLAS]: Generiere Sektor -> {section_title} (Versuch {attempt + 1}) ...")
                response = ollama.generate(
                    model=MODEL_NAME,
                    prompt=f"{system_prompt}\n\n{full_prompt}",
                    stream=False
                )
                return response.get("response", "[COMPILER_ERROR: Keine Antwort]")
            except Exception as e:
                logger.warning(f"Versuch {attempt + 1} fehlgeschlagen für {section_title}: {e}")
                if attempt < 2:
                    time.sleep(5)  # Wait for server recovery
                else:
                    logger.error(f"SYSTEM-ERROR nach 3 Versuchen bei {section_title}: {e}")
                    return f"SYSTEM-ERROR bei Generierung: {e}"
        return "[COMPILER_ERROR: Unbekannter Fehler]"

    def run_compilation(self) -> None:
        """Iterates through the taxonomy and compiles the documentation into markdown files."""
        for chapter, topics in DOCUMENT_TAXONOMY.items():
            chapter_path = os.path.join(DOCS_OUTPUT_DIR, f"{chapter}.md")
            
            logger.info(f"[ATLAS]: Starte Kompilierung Kapitel: {chapter}")
            try:
                with open(chapter_path, "w", encoding="utf-8") as f:
                    f.write(f"# {chapter.replace('_', ' ')}\n\n")
                    
                    for index, topic in enumerate(topics):
                        section_title = f"Sektion {index + 1}"
                        content = self._generate_section(section_title, topic)
                        f.write(f"## {section_title}\n\n{content}\n\n---\n\n")
                        time.sleep(1)  # Latency buffer for thermal stability and API throttling
                
                logger.success(f"[ATLAS]: Kapitel {chapter} versiegelt. -> {chapter_path}")
            except Exception as e:
                logger.critical(f"Kritischer Fehler beim Schreiben von {chapter_path}: {e}")

if __name__ == "__main__":
    compiler = DocCompiler()
    compiler.run_compilation()
    logger.info(f"[ATLAS]: Kompilierung abgeschlossen. Dokumente in {DOCS_OUTPUT_DIR} verfügbar.")
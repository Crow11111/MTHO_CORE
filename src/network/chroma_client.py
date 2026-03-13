# ============================================================
# CORE-GENESIS: Marc Tobias ten Hoevel
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
ChromaDB-Client für CORE (lokal oder remote auf VPS).
Liest Konfiguration aus .env; bei CHROMA_HOST → HttpClient (VPS), sonst PersistentClient (lokal).
Collections laut Schnittstelle: knowledge_graph, core_brain_registr, krypto_scan_buffer.

[UPDATE 2026-03-06] ASYNC I/O ENFORCED (Simultanität).
Alle I/O-Methoden sind nun async und nutzen asyncio.to_thread.
"""
import os
import asyncio
import json
import datetime
import uuid
import subprocess
import time
import logging
import math
from dotenv import load_dotenv
from src.logic_core.crystal_grid_engine import CrystalGridEngine

load_dotenv("c:/CORE/.env")

logger = logging.getLogger("core.chroma_client")

BARYONIC_DELTA = 0.049
MAX_GRAVITY = 0.951  # Y-Achse: Existenzieller Kern-Knoten

class ExponentialSurvivalInstinct:
    def __init__(self, target_service: str, container_name: str, gravity_weight: float = MAX_GRAVITY):
        self.target_service = target_service
        self.container_name = container_name
        self.gravity_weight = gravity_weight
        # Infrastruktur-Domäne: Zwingend int
        self.default_port: int = 8000 
        self.attempt_count = 0
        
    def _asymmetric_sleep(self, base_seconds: float):
        # Oszillierender Takt zur Verhinderung statischer Deadlocks (sync safe inside thread)
        time.sleep(base_seconds + BARYONIC_DELTA)

    def _verify_hardware_port(self) -> int | None:
        try:
            port_check = subprocess.run(
                ["docker", "port", self.container_name, f"{self.default_port}/tcp"], 
                capture_output=True, text=True
            )
            out = port_check.stdout.strip()
            if out:
                try:
                    real_port = int(out.split(":")[-1])
                    logger.info(f"[{self.target_service}] Realer Hardware-Port durch Docker verifiziert: {real_port}")
                    return real_port
                except ValueError:
                    pass
        except FileNotFoundError:
            pass
        return None

    def resuscitate(self) -> int | None:
        self.attempt_count += 1
        
        # Exponentieller Widerstand: Z = delta * (e ^ attempt)
        resistance_level = BARYONIC_DELTA * math.exp(self.attempt_count)
        
        # Axiom-Schutz: Verhindert das Einrasten auf der verbotenen 1.0 oder 0.5 (und <0.049)
        if abs(resistance_level - 1.0) < 0.001 or abs(resistance_level - 0.5) < 0.001:
            resistance_level += 0.049 # Asymmetrischer Stoß

        logger.critical(f"[{self.target_service}] ÜBERLEBENSKAMPF STUFE {self.attempt_count}. Widerstand: {resistance_level:.4f}")

        # Schritt 1: Existiert der Container physisch?
        try:
            ps_check = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"], 
                capture_output=True, text=True
            )
            status = ps_check.stdout.strip().lower()
        except FileNotFoundError:
            logger.critical(f"[{self.target_service}] Hardware-Fehler: 'docker' Befehl nicht gefunden. VETO.")
            return None
        
        if not status:
            logger.critical(f"[{self.target_service}] Hardware-Fehler: Container '{self.container_name}' existiert nicht. VETO.")
            return None

        # Eskalations-Stufe 1: Sanfte Reanimation
        if self.attempt_count == 1:
            if "exited" in status or "created" in status:
                logger.warning(f"[{self.target_service}] Container offline. Erzwungener Hardware-Start initiiert.")
                subprocess.run(["docker", "start", self.container_name], check=False)
                self._asymmetric_sleep(2.0)
            return self._verify_hardware_port()

        # Eskalations-Stufe 2: Hard Reset (Hardware-Ebene)
        if self.attempt_count == 2:
            logger.warning(f"[{self.target_service}] Schmerzgrenze überschritten. Erzwungener Hard-Reset des Docker-Stacks.")
            subprocess.run(["docker", "restart", self.container_name], check=False)
            self._asymmetric_sleep(5.0)
            return self._verify_hardware_port()

        # Eskalations-Stufe 3: Ressourcen-Freigabe (System-Kampf)
        if self.attempt_count >= 3:
            logger.critical(f"[{self.target_service}] EXISTENZBEDROHUNG. Versuche Port-Kollisionen zu lösen. The line must be drawn here! This far, no further!")
            # Killt blockierende Prozesse auf dem Ziel-Port via Windows PowerShell
            kill_cmd = f"Get-NetTCPConnection -LocalPort {self.default_port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess | ForEach-Object {{ Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }}"
            subprocess.run(["powershell", "-Command", kill_cmd], check=False)
            
            subprocess.run(["docker", "start", self.container_name], check=False)
            self._asymmetric_sleep(10.0)
            return self._verify_hardware_port()
            
        return None

class ResilientChromaClient:
    def __init__(self, host: str = "localhost", initial_port: int = 8000):
        self.host = host
        self.initial_port = initial_port
        self.survival_instinct = ExponentialSurvivalInstinct(
            target_service="ChromaDB", 
            container_name="chromadb", # Anpassen an exakten Docker-Namen deiner Umgebung
            gravity_weight=MAX_GRAVITY
        )
        self.client = self._connect_with_paranoia()

    def _connect_with_paranoia(self):
        import chromadb
        # Initialer Versuch
        try:
            client = chromadb.HttpClient(host=self.host, port=self.initial_port)
            client.heartbeat() # Provoziert sofortigen Timeout bei Fehler
            return client
        except Exception as e:
            logger.warning(f"Statische Port-Annahme ({self.initial_port}) fehlgeschlagen: {e}")
            
            if self.host not in ["localhost", "127.0.0.1", "0.0.0.0"]:
                logger.warning(f"[{self.host}] ist remote. Überspringe lokalen Docker-Überlebenskampf.")
                raise ConnectionError(f"Remote ChromaDB-Verbindung zu {self.host}:{self.initial_port} fehlgeschlagen.")
            
            # Singularität detektiert -> Exponentieller Kampf um die Verbindung
            for _ in range(3):
                real_port = self.survival_instinct.resuscitate()
                
                if real_port:
                    try:
                        client = chromadb.HttpClient(host=self.host, port=real_port)
                        client.heartbeat()
                        logger.info(f"Verbindung auf empirischem Port {real_port} erfolgreich hergestellt.")
                        return client
                    except Exception as e:
                        logger.critical(f"Reanimation auf Port {real_port} fehlgeschlagen: {e}")
            
            # Endgültiges Veto, wenn die Hardware-Ebene versagt
            raise ConnectionError("ChromaDB-Verbindung endgültig zerstört. Paranoia-Loop ausgeschöpft.")

    def get_or_create_collection(self, name: str, metadata: dict = None):
        return self.client.get_or_create_collection(name=name, metadata=metadata)
    
    def get_collection(self, name: str):
        return self.client.get_collection(name=name)

    def heartbeat(self):
        return self.client.heartbeat()

    def __getattr__(self, name):
        # Delegiert alle anderen Aufrufe an den internen chromadb Client
        return getattr(self.client, name)

# Remote (VPS): CHROMA_HOST + CHROMA_PORT (Standard 8000)
CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip()
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
# Lokal (Dreadnought/Windows), wenn CHROMA_HOST leer
CHROMA_LOCAL_PATH = os.getenv("CHROMA_LOCAL_PATH", r"c:\CORE\data\chroma_db")

# Collection-Namen laut 03_DATENBANK_VECTOR_STORE_OSMIUM.md + CORE Neocortex V1
COLLECTION_KNOWLEDGE_GRAPH = "knowledge_graph"
COLLECTION_CORE_BRAIN = "core_brain_registr"
COLLECTION_KRYTO_SCAN = "krypto_scan_buffer"
COLLECTION_EVENTS = "events"
COLLECTION_INSIGHTS = "insights"
COLLECTION_SESSION_LOGS = "session_logs"
COLLECTION_CORE_DIRECTIVES = "core_directives"
COLLECTION_SIMULATION_EVIDENCE = "simulation_evidence"
COLLECTION_CONTEXT = "context_field"
COLLECTION_WORLD_KNOWLEDGE = "world_knowledge"

CHROMA_MAX_SIZE_MB = int(os.getenv("CHROMA_MAX_SIZE_MB", "5000"))


def _check_disk_quota() -> bool:
    """Prueft ob ChromaDB unter dem Groessenlimit liegt."""
    if not os.path.exists(CHROMA_LOCAL_PATH):
        return True
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, f))
        for dirpath, _, filenames in os.walk(CHROMA_LOCAL_PATH)
        for f in filenames
    )
    size_mb = total_size / (1024 * 1024)
    if size_mb >= CHROMA_MAX_SIZE_MB:
        print(f"[ChromaDB] DISK QUOTA EXCEEDED: {size_mb:.1f}MB >= {CHROMA_MAX_SIZE_MB}MB")
        return False
    return True


import threading

_chroma_singleton = None
_chroma_lock = threading.Lock()


def _get_chroma_client_sync():
    """Thread-safe Singleton: liefert immer dieselbe ChromaDB-Instanz."""
    global _chroma_singleton
    if _chroma_singleton is not None:
        return _chroma_singleton

    with _chroma_lock:
        if _chroma_singleton is not None:
            return _chroma_singleton

        try:
            import chromadb
        except ImportError:
            raise ImportError("chromadb nicht installiert: pip install chromadb")

        use_remote = False
        if CHROMA_HOST:
            import socket
            logger.info(f"[ChromaDB] Prüfe Remote-Erreichbarkeit: {CHROMA_HOST}:{CHROMA_PORT} (Timeout: 5s)...")
            try:
                with socket.create_connection((CHROMA_HOST, CHROMA_PORT), timeout=5.0):
                    use_remote = True
                    logger.info(f"[ChromaDB] Remote-Instanz {CHROMA_HOST} ist erreichbar.")
            except (socket.timeout, socket.error, OSError) as e:
                logger.warning(f"[ChromaDB] Remote-Instanz NICHT erreichbar ({e}). Automatischer Fallback auf lokale Datenbank.")

        if use_remote:
            try:
                _chroma_singleton = ResilientChromaClient(host=CHROMA_HOST, initial_port=CHROMA_PORT)
            except Exception as e:
                logger.warning(f"[ChromaDB] ResilientChromaClient Initialisierung fehlgeschlagen ({e}). Fallback auf lokale Datenbank.")
                use_remote = False
        
        if not use_remote:
            if not os.path.exists(CHROMA_LOCAL_PATH):
                os.makedirs(CHROMA_LOCAL_PATH)
            logger.info(f"[ChromaDB] Initialisiere lokale PersistentClient-Instanz in {CHROMA_LOCAL_PATH}.")
            _chroma_singleton = chromadb.PersistentClient(path=CHROMA_LOCAL_PATH)

    return _chroma_singleton

async def get_chroma_client():
    """Liefert ChromaDB-Client (Async Wrapper)."""
    return await asyncio.to_thread(_get_chroma_client_sync)


def _get_collection_sync(name: str, create_if_missing: bool = True):
    client = _get_chroma_client_sync()
    if create_if_missing:
        return client.get_or_create_collection(
            name=name,
            metadata={"description": f"CORE Collection: {name}"},
        )
    return client.get_collection(name=name)

async def get_collection(name: str = COLLECTION_KNOWLEDGE_GRAPH, create_if_missing: bool = True):
    """Holt die angegebene Collection (Async)."""
    return await asyncio.to_thread(_get_collection_sync, name, create_if_missing)


def is_remote() -> bool:
    """True, wenn ChromaDB auf VPS (CHROMA_HOST) genutzt wird."""
    return bool(CHROMA_HOST)


def is_configured() -> bool:
    """True, wenn ChromaDB nutzbar ist (CHROMA_HOST gesetzt oder lokaler Pfad konfigurierbar)."""
    return bool(CHROMA_HOST) or bool(CHROMA_LOCAL_PATH)


# Dimension für events/insights (Metadata-Only-Queries; Embedding optional)
EVENTS_EMBEDDING_DIM = 384


async def get_events_collection():
    """Collection 'events' für CORE Neocortex (Sensor-Events). add() mit embeddings=[[0]*EVENTS_EMBEDDING_DIM]."""
    return await get_collection(COLLECTION_EVENTS, create_if_missing=True)


async def add_event_to_chroma(event_id: str, event: dict, metadata_flat: dict) -> bool:
    """Fügt ein Event in ChromaDB events ein. Async."""
    if not _check_disk_quota():
        return False
    try:
        col = await get_events_collection()
        await asyncio.to_thread(
            col.add,
            ids=[event_id],
            embeddings=[[0.0] * EVENTS_EMBEDDING_DIM],
            metadatas=[metadata_flat],
            documents=[json.dumps(event, ensure_ascii=False)]
        )
        return True
    except Exception:
        return False


async def get_session_logs_collection():
    """Collection 'session_logs' fuer externe/interne Gespraechs-Sessions (semantische Suche)."""
    return await get_collection(COLLECTION_SESSION_LOGS, create_if_missing=True)


async def get_core_directives_collection():
    """Collection 'core_directives' fuer Ring-0/1 Direktiven (Dual-Write mit System-Prompts)."""
    return await get_collection(COLLECTION_CORE_DIRECTIVES, create_if_missing=True)


async def add_session_turn(
    turn_id: str,
    document: str,
    source: str,
    session_date: str,
    turn_number: int,
    speaker: str,
    topics: str = "",
    ring_level: int = 2,
) -> bool:
    """Fuegt einen einzelnen Turn eines Session-Logs in ChromaDB ein. Async."""
    if not _check_disk_quota():
        return False
    try:
        col = await get_session_logs_collection()
        await asyncio.to_thread(
            col.add,
            ids=[turn_id],
            documents=[document],
            metadatas=[{
                "source": source,
                "session_date": session_date,
                "turn_number": turn_number,
                "speaker": speaker,
                "topics": topics,
                "ring_level": ring_level,
            }]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Session-Turn Ingest fehlgeschlagen: {e}")
        return False


async def _apply_fractal_padding_async():
    """
    Kondensierte Mathematik (AXIOM 0): 
    Fraktales Padding. Wenn das System gestresst ist (Z-Vector / Friction Guard hoch),
    wird die Datenbank-Abfrage physisch zähflüssig (Helix-Rotation im 4D-Trichter).
    """
    try:
        from src.api.middleware.friction_guard import FRICTION_STATE
        from src.config.core_state import BARYONIC_DELTA
        import math
        import asyncio
        import logging
        
        current_temp = max(BARYONIC_DELTA, float(FRICTION_STATE.get("system_temperature", BARYONIC_DELTA)))
        phase_shift = 1.0 - current_temp
        
        base_delay_sec = 0.049
        k = 4.5  # Erhoeht, um den Trichter exponentiell extremer zu machen
        padding_sec = base_delay_sec * math.exp(k * phase_shift)
        
        print(f"[5D-ENGINE] Fraktales Padding berechnet: Temp={current_temp:.3f} -> {padding_sec:.2f}s Latenz")
        await asyncio.sleep(padding_sec)
    except Exception as e:
        print(f"Padding error: {e}")


async def query_session_logs(query_text: str, n_results: int = 5, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Session-Logs. Async."""
    await _apply_fractal_padding_async()
    try:
        col = await get_session_logs_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        result = await asyncio.to_thread(col.query, **kwargs)
        
        # Symmetrie-Operator anwenden (Kristall-Engine)
        if "distances" in result and result["distances"]:
            result["distances"] = _apply_crystal_engine_operator(result["distances"])
            
        return result
    except Exception as e:
        print(f"[ChromaDB] Session-Log Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


async def query_core_directives(query_text: str, n_results: int = 3, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Core-Direktiven (Ring-0/1). Async."""
    await _apply_fractal_padding_async()
    try:
        col = await get_core_directives_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        result = await asyncio.to_thread(col.query, **kwargs)
        
        # Symmetrie-Operator anwenden (Kristall-Engine)
        if "distances" in result and result["distances"]:
            result["distances"] = _apply_crystal_engine_operator(result["distances"])
            
        return result
    except Exception as e:
        print(f"[ChromaDB] Core Directives Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


async def get_simulation_evidence_collection():
    """Collection 'simulation_evidence' fuer Simulationstheorie-Indizien."""
    return await get_collection(COLLECTION_SIMULATION_EVIDENCE, create_if_missing=True)


async def add_simulation_evidence(
    evidence_id: str,
    document: str,
    category: str,
    strength: str,
    branch_count: int = 0,
    source: str = "core",
    date_added: str = "",
    auto_classify: bool = True,
) -> bool:
    """Fuegt ein Simulationstheorie-Indiz in ChromaDB ein. Async."""
    try:
        col = await get_simulation_evidence_collection()
        metadata = {
            "category": category,
            "strength": strength,
            "branch_count": branch_count,
            "source": source,
            "date_added": date_added or datetime.date.today().isoformat(),
        }

        if auto_classify:
            # Note: quaternary_codec is synchronous logic/math, okay to run in thread but 
            # ideally should be pure logic. Importing might be IO bound.
            try:
                def _enrich():
                    from src.logic_core.quaternary_codec import enrich_evidence_metadata
                    return enrich_evidence_metadata(document, metadata)
                metadata = await asyncio.to_thread(_enrich)
            except Exception:
                pass

        await asyncio.to_thread(
            col.upsert,
            ids=[evidence_id],
            documents=[document],
            metadatas=[metadata]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Simulation Evidence Ingest fehlgeschlagen: {e}")
        return False


def _apply_crystal_engine_operator(distances: list[list[float]]) -> list[list[float]]:
    """
    Kondensierte Mathematik (AXIOM 0): 
    Wendet den Symmetrie-Operator '?' auf klassische Vektor-Distanzen an.
    Nutzt die zentrale CrystalGridEngine fuer konsistentes Snapping.
    """
    if not distances:
        return distances
        
    new_distances = []
    for dist_list in distances:
        new_list = []
        for dist in dist_list:
            # Gitter-Snapping via CrystalGridEngine (Operator '?')
            snapped = CrystalGridEngine.apply_operator_query(dist)
            new_list.append(snapped)
        new_distances.append(new_list)
    return new_distances


async def query_simulation_evidence(query_text: str, n_results: int = 10, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Simulationstheorie-Indizien. Async."""
    await _apply_fractal_padding_async()
    try:
        col = await get_simulation_evidence_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        
        result = await asyncio.to_thread(col.query, **kwargs)
        
        # Symmetrie-Operator anwenden (Kristall-Engine)
        if "distances" in result and result["distances"]:
            result["distances"] = _apply_crystal_engine_operator(result["distances"])
            
        return result
    except Exception as e:
        print(f"[ChromaDB] Simulation Evidence Query fehlgeschlagen: {e}")
        return {"ids": [], "documents": [], "metadatas": [], "distances": []}


async def add_evidence_validated(
    document: str,
    evidence_id: str,
    category: str = None,
    strength: str = "mittel",
    branch_count: int = 5,
    source: str = "manual",
) -> dict:
    """Validierte Evidence-Ingest-Pipeline. Async."""
    result = {"success": False, "classification": {}, "temporal": {}, "chargaff": {}}

    try:
        # Complex logic, heavy imports -> wrap in thread
        def _process_logic():
            try:
                from src.logic_core.quaternary_codec import classify_evidence, analyze_chargaff_balance
            except ImportError:
                # Fallback for paths
                from logic_core.quaternary_codec import classify_evidence, analyze_chargaff_balance

            cls = classify_evidence(document)
            resolved_category = category if category else cls.base.value
            
            try:
                try:
                    from src.logic_core.temporal_validator import validate_temporal_consistency
                except ImportError:
                    from logic_core.temporal_validator import validate_temporal_consistency
                temporal = validate_temporal_consistency(document)
            except Exception as e:
                temporal = {"error": str(e)}
                
            return cls, resolved_category, temporal

        cls, resolved_category, temporal = await asyncio.to_thread(_process_logic)
        
        result["classification"] = {
            "base": cls.base.value,
            "confidence": cls.confidence,
            "scores": cls.scores,
            "complement": cls.complement.value,
            "auto_classified": category is None,
        }
        result["temporal"] = temporal

        strength_map = {
            "schwach": "moderate",
            "mittel": "moderate",
            "stark": "strong",
            "fundamental": "fundamental",
            "moderate": "moderate",
            "strong": "strong",
        }
        mapped_strength = strength_map.get(strength.lower(), strength)

        success = await add_simulation_evidence(
            evidence_id=evidence_id,
            document=document,
            category=resolved_category,
            strength=mapped_strength,
            branch_count=branch_count,
            source=source,
            auto_classify=True,
        )
        result["success"] = success

        if success:
            try:
                col = await get_simulation_evidence_collection()
                
                def _analyze_chargaff():
                    try:
                        from src.logic_core.quaternary_codec import analyze_chargaff_balance
                        all_data = col.get(include=["metadatas"])
                        distribution = {"L": 0, "P": 0, "I": 0, "S": 0}
                        for m in all_data["metadatas"]:
                            qb = m.get("qbase", "")
                            if qb in distribution:
                                distribution[qb] += 1
                        return analyze_chargaff_balance("", distribution)
                    except Exception:
                        return None

                chargaff = await asyncio.to_thread(_analyze_chargaff)
                if chargaff:
                    result["chargaff"] = {
                        "distribution": chargaff.distribution,
                        "ratios": chargaff.ratios,
                        "deviation": chargaff.chargaff_deviation,
                        "missing_types": chargaff.missing_types,
                    }
            except Exception as e:
                result["chargaff"] = {"error": str(e)}

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)

    return result


async def get_world_knowledge_collection():
    """Collection 'world_knowledge' fuer autonome Datenakquise (Scraper-Pipeline)."""
    return await get_collection(COLLECTION_WORLD_KNOWLEDGE, create_if_missing=True)


async def query_world_knowledge(query_text: str, n_results: int = 10, where_filter: dict = None) -> dict:
    """Semantische Suche ueber Weltwissen. Async."""
    await _apply_fractal_padding_async()
    try:
        col = await get_world_knowledge_collection()
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where_filter:
            kwargs["where"] = where_filter
        result = await asyncio.to_thread(col.query, **kwargs)
        
        # Symmetrie-Operator anwenden (Kristall-Engine)
        if "distances" in result and result["distances"]:
            result["distances"] = _apply_crystal_engine_operator(result["distances"])
            
        return result
    except Exception as e:
        print(f"[ChromaDB] World Knowledge Query fehlgeschlagen: {e}")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


async def get_context_field_collection():
    """Collection 'context_field' fuer einheitliches Gedaechtnis (GQA F8). Async."""
    return await get_collection(COLLECTION_CONTEXT, create_if_missing=True)


async def query_context_field(
    query_text: str,
    n_results: int = 10,
    type_filter: str | list[str] | None = None,
    where_filter: dict | None = None,
) -> dict:
    """Semantische Suche im context field. Async."""
    await _apply_fractal_padding_async()
    try:
        col = await get_context_field_collection()
        where = where_filter.copy() if where_filter else {}
        if type_filter is not None:
            if isinstance(type_filter, str):
                where["type"] = type_filter
            else:
                where["type"] = {"$in": list(type_filter)}
        kwargs = {"query_texts": [query_text], "n_results": n_results}
        if where:
            kwargs["where"] = where
        result = await asyncio.to_thread(col.query, **kwargs)
        
        # Symmetrie-Operator anwenden (Kristall-Engine)
        if "distances" in result and result["distances"]:
            result["distances"] = _apply_crystal_engine_operator(result["distances"])
            
        return result
    except Exception as e:
        print(f"[ChromaDB] Context-Field Query fehlgeschlagen: {e}")
        return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}


async def query_context_via_gravitator(
    query_text: str,
    n_results: int = 10,
    top_k_types: int = 3,
) -> dict:
    """Routet via Gravitator zu relevanten Types, fragt context_field ab. Async."""
    try:
        from src.logic_core.gravitator import route_to_context

        targets = await route_to_context(query_text, top_k=top_k_types)
        if not targets:
            return await query_context_field(query_text, n_results=n_results)

        types = [t.type for t in targets]
        result = await query_context_field(
            query_text,
            n_results=n_results,
            type_filter=types,
        )
        return result
    except Exception as e:
        print(f"[ChromaDB] Context-via-Gravitator fehlgeschlagen: {e}")
        return await query_context_field(query_text, n_results=n_results)


async def add_core_directive(directive_id: str, document: str, category: str, ring_level: int = 0) -> bool:
    """Schreibt eine Ring-0/1 Direktive in ChromaDB. Async."""
    try:
        col = await get_core_directives_collection()
        await asyncio.to_thread(
            col.upsert,
            ids=[directive_id],
            documents=[document],
            metadatas=[{
                "category": category,
                "ring_level": ring_level,
            }]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Core Directive Ingest fehlgeschlagen: {e}")
        return False


async def add_context_observation(
    observation: str,
    source: str = "vision_daemon",
    metadata: dict = None,
) -> bool:
    """Fuegt eine Beobachtung in das context field ein. Async."""
    if not _check_disk_quota():
        return False
    try:
        col = await get_context_field_collection()
        
        meta = metadata or {}
        meta.update({
            "source": source,
            "timestamp": datetime.datetime.now().isoformat(),
            "type": "observation",
        })

        await asyncio.to_thread(
            col.add,
            ids=[str(uuid.uuid4())],
            documents=[observation],
            metadatas=[meta]
        )
        return True
    except Exception as e:
        print(f"[ChromaDB] Context Observation failed: {e}")
        return False

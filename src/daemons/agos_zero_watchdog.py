# ============================================================
# CORE-GENESIS: ZERO WATCHDOG (BUILD_SYSTEM HARDENED)
# VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
# LOGIC: 2-2-1-0 (NON-BINARY)
# ============================================================

"""
ZERO WATCHDOG (Der intrinsische Beobachter).
Ersetzt den manuellen Trigger durch physikalische Realitaets-Checks.

PROTOCOL: HEPHAISTOS_ANCHOR_V1
1. Entropy Check: Ping (Latenz > 0ms beweist Existenz)
2. Git Alignment Check: Git Remote vs Local (Drift beweist Zeitfluss)
3. Friction Injection: Sendet keine Mocks, sondern echte Messdaten.
"""

import asyncio
import json
import os
import sys
import tempfile
import time
import httpx
import subprocess
import re
from typing import Dict, Any, Optional
from loguru import logger
from dotenv import dotenv_values

# Import Core Constants
sys.path.append(os.getcwd())
# Versuche Konstanten zu laden, Fallback auf Hardcoded wenn Module fehlen
try:
    from src.config.core_state import BARYONIC_DELTA, SYMMETRY_BREAK
    from src.logic_core.crystal_grid_engine import CrystalGridEngine
except ImportError:
    BARYONIC_DELTA = 0.049
    SYMMETRY_BREAK = 0.49
    class CrystalGridEngine:
        @staticmethod
        def apply_operator_query(v): return 0.049 if v < 0.049 else v
        @staticmethod
        def calculate_resonance(a, b): return 0.951

# Konfiguration
WATCHDOG_INTERVAL = 61.0  # Sekunden (Herzschlag) - Primzahl für Zikaden-Prinzip
REMOTE_CHECK_INTERVAL = 300.0 # Alle 5 Min Git Check (teuer)
TELEMETRY_PATH = os.path.join(os.getenv("CORE_DATA_DIR", "c:/CORE/data"), "telemetry.json")

# Environment
env_vars = dotenv_values(".env")
API_URL = os.getenv("CORE_VPS_URL", "http://localhost:8000")
WEBHOOK_URL = f"{API_URL}/webhook/omega_thought"
HEADERS = {"Authorization": f"Bearer {env_vars.get('HA_WEBHOOK_TOKEN', '')}"}

# Status-Speicher
SYSTEM_STATE = {
    "last_friction_time": 0.0,
    "last_git_check": 0.0,
    "last_latency_ms": 0.0,
    "git_drift": "UNKNOWN", # SYNCED, AHEAD, BEHIND, DETACHED
    "mode": "BOOT"
}

async def check_connectivity() -> float:
    """
    Misst die Netzwerk-Latenz zu einem externen Anker (Google DNS).
    Liefert RTT in ms. -1.0 bei Fehler (kein Netz).
    """
    host = "8.8.8.8"
    param = "-n" if sys.platform.lower() == "win32" else "-c"
    command = ["ping", param, "1", host]

    try:
        # Führe Ping aus
        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        end = time.perf_counter()

        if proc.returncode == 0:
            # Versuche echte Zeit aus Output zu parsen (Genauer)
            # Windows: "Zeit=14ms", Linux: "time=14.2 ms"
            output = stdout.decode('utf-8', errors='ignore')
            match = re.search(r"(?:Zeit|time)[=<]([\d\.]+)\s?ms", output)
            if match:
                val = float(match.group(1))
            else:
                # Fallback: Wall Clock Time (ungenau, aber > 0)
                val = (end - start) * 1000.0
            
            # Topologische Resonanz-Pruefung der Latenz
            # Wir mappen die Latenz (ms) auf einen Resonanz-Wert [0..1]
            # 10ms -> 0.951 (Lock), 100ms -> 0.49 (Symmetry Break), 500ms -> 0.049 (Delta)
            norm_latency = max(0.0, min(1.0, 1.0 - (val / 500.0)))
            resonance = CrystalGridEngine.apply_operator_query(norm_latency)
            SYSTEM_STATE["last_resonance"] = resonance
            return val
        else:
            logger.warning(f"[WATCHDOG] Entropy-Check failed (No Internet?): {stderr.decode().strip()}")
            SYSTEM_STATE["last_resonance"] = BARYONIC_DELTA
            return -1.0 # Void State

    except Exception as e:
        logger.error(f"[WATCHDOG] Ping Error: {e}")
        return -1.0

async def check_git_alignment() -> str:
    """
    Prüft die Synchronisation mit dem Git-Remote.
    Drift = Friction.
    """
    try:
        # 1. Local Hash
        local_proc = await asyncio.create_subprocess_exec(
            "git", "rev-parse", "HEAD",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out_local, _ = await local_proc.communicate()
        local_hash = out_local.decode().strip()

        # 2. Remote Hash (Teuer, Netzwerk)
        # Wir nutzen ls-remote um keinen lokalen State zu ändern
        remote_proc = await asyncio.create_subprocess_exec(
            "git", "ls-remote", "origin", "HEAD",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        out_remote, _ = await remote_proc.communicate()
        # Output format: "<hash>\tHEAD"
        remote_parts = out_remote.decode().strip().split()
        if not remote_parts:
            return "OFFLINE"

        remote_hash = remote_parts[0]

        if local_hash == remote_hash:
            return "SYNCED"
        else:
            return "DESYNC"

    except Exception as e:
        logger.error(f"[WATCHDOG] Git Check Failed: {e}")
        return "ERROR"

async def check_vital_signs():
    """Prüft, ob der API-Body (localhost) antwortet."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{API_URL}/status", timeout=5.0)
            return resp.status_code == 200
    except Exception:
        return False

async def inject_reality_anchor(friction_data: Dict[str, Any]):
    """
    Injiziert den gemessenen Reibungs-Vektor in den Cortex.
    Keine 'Gedanken' mehr, sondern rohe Telemetrie.
    """
    latency = friction_data.get('latency_ms', -1)
    git_status = friction_data.get('git_status', 'UNKNOWN')
    resonance = friction_data.get('resonance', 0.049)

    # Nachricht basierend auf Fakten konstruieren
    if resonance <= BARYONIC_DELTA:
        thought = "WARNUNG: System-Resonanz am Baryonischen Limit (Λ). Kristall-Gitter instabil."
        context = "CRYSTAL_BREACH"
    elif resonance >= 0.951:
        thought = f"Resonanz-Lock (0.951) erreicht. Gitter stabil. Latenz: {latency:.1f}ms."
        context = "RESONANCE_LOCK"
    elif git_status == "DESYNC":
        thought = f"Git-Synchronisations-Divergenz erkannt. Status: {git_status}. Push/Pull empfohlen."
        context = "GIT_DESYNC"
    else:
        thought = f"Reality Check: {latency:.1f}ms Latenz. Resonanz: {resonance:.3f}."
        context = "ANCHOR_HEARTBEAT"

    payload = {
        "thought": thought,
        "context": {
            "type": context,
            "source": "ZERO_WATCHDOG_HEPHAISTOS",
            "telemetry": friction_data
        },
        "sender": "SYSTEM_WATCHDOG",
        "require_response": False # Nur Info, keine zwingende Antwort
    }

    is_localhost = "localhost" in WEBHOOK_URL or "127.0.0.1" in WEBHOOK_URL
    try:
        from src.utils.time_metric import get_friction_timeout
        async with httpx.AsyncClient(verify=not is_localhost) as client:
            timeout_friction = get_friction_timeout(10.0)
            await client.post(WEBHOOK_URL, json=payload, headers=HEADERS, timeout=timeout_friction)
            logger.info(f"[WATCHDOG] Reality Injected: {context} | {latency:.1f}ms")
            SYSTEM_STATE["last_friction_time"] = time.time()
    except Exception as e:
        logger.error(f"[WATCHDOG] Injection failed: {e}")

async def watchdog_loop():
    logger.info("ZERO WATCHDOG (BUILD_SYSTEM EDITION) gestartet.")
    logger.info(f"Target: {API_URL} | Interval: {WATCHDOG_INTERVAL}s")

    # Initial Wait for Body
    while not await check_vital_signs():
        logger.warning("[WATCHDOG] Warte auf Körper (API)...")
        await asyncio.sleep(5)

    SYSTEM_STATE["mode"] = "WATCH"

    while True:
        current_time = time.time()

        # 1. Physics Check (Ping)
        latency = await check_connectivity()
        SYSTEM_STATE["last_latency_ms"] = latency

        # 2. Git Alignment Check - seltener
        if current_time - SYSTEM_STATE["last_git_check"] > REMOTE_CHECK_INTERVAL:
            git_status = await check_git_alignment()
            SYSTEM_STATE["git_drift"] = git_status
            SYSTEM_STATE["last_git_check"] = current_time
            logger.info(f"[WATCHDOG] Git Alignment: {git_status}")
        else:
            git_status = SYSTEM_STATE["git_drift"]

        # 3. Logik: Brauchen wir Friction?
        # Wenn Drift da ist -> SOFORT melden
        # Wenn Latenz weg ist -> SOFORT melden
        # Sonst -> Herzschlag alle X Minuten

        urgent = False
        if git_status == "DESYNC":
            urgent = True
        if latency < 0:
            urgent = True

        # Wenn urgent oder Zeit abgelaufen (Heartbeat alle 5 Min)
        time_since_friction = current_time - SYSTEM_STATE["last_friction_time"]
        if urgent or (time_since_friction > 300):
            friction_data = {
                "latency_ms": latency,
                "git_status": git_status,
                "resonance": SYSTEM_STATE.get("last_resonance", 0.049),
                "timestamp": current_time
            }
            await inject_reality_anchor(friction_data)

        _write_telemetry(latency, git_status, SYSTEM_STATE.get("last_resonance", 0.049))

        logger.debug(f"[WATCHDOG] Tick. Latency: {latency:.1f}ms | Git: {git_status}")

        from src.utils.time_metric import asym_sleep_float_async
        await asym_sleep_float_async(WATCHDOG_INTERVAL)


def _write_telemetry(latency_ms: float, git_status: str, resonance: float):
    """Schreibt Telemetrie atomar via os.replace (kein partial read)."""
    data = {
        "latency_ms": round(latency_ms, 1),
        "git_status": git_status,
        "resonance": round(resonance, 3),
        "mode": SYSTEM_STATE.get("mode", "UNKNOWN"),
        "timestamp": time.time(),
    }
    os.makedirs(os.path.dirname(TELEMETRY_PATH), exist_ok=True)
    tmp_path = TELEMETRY_PATH + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.replace(tmp_path, TELEMETRY_PATH)
    except Exception as e:
        logger.warning(f"[WATCHDOG] Telemetry-Write fehlgeschlagen: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        os.environ["PYTHONIOENCODING"] = "utf-8"
        # Windows Proactor Loop Fix für Subprozesse
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(watchdog_loop())
    except KeyboardInterrupt:
        logger.info("[WATCHDOG] Beendet durch User (SIGINT).")

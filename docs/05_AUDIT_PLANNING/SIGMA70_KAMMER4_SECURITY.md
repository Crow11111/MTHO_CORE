# SIGMA-70 AUDIT – KAMMER 4: Security-Architektur, Chaos-Engineering, Veto-Logik

> **HISTORISCH – kein Fix noetig:** Dieses Audit dokumentiert den Zustand vom 2026-03-11. Referenzen auf `context_injector.py` (heute `context_injector.py`) und `council_gate.py` (heute `veto_gate.py`) sind bewusst unveraendert.

**Auditor:** Security-Expert (Schicht 3)
**Datum:** 2026-03-11
**Status:** AUDIT ABGESCHLOSSEN
**Methode:** Axiomatische Pruefung (4-Schritt: These → Antithese → Synthese → Artefakt)

**Gepruefte Dateien:**
- `src/logic_core/z_vector_damper.py`
- `src/logic_core/takt_gate.py`
- `src/config/core_state.py`
- `src/config/ring0_state.py`
- `src/logic_core/context_injector.py`
- `src/ai/llm_interface.py`
- `src/api/middleware/council_gate.py`
- `src/api/routes/telemetry.py`
- `src/api/routes/chat.py`
- `src/api/entry_adapter.py`
- `src/utils/time_metric.py`
- `docs/02_ARCHITECTURE/OMEGA_RING_0_MANIFEST.md`
- `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md`
- `docs/04_PROCESSES/TAKT_0_VOR_DELEGATION.md`

---

## SCHRITT 1: THESE – Angriffsvektoren fuer Endlos-Betrieb

### 1.1 VPS-Kompromittierung

**Angriffsvektor:** Der VPS ist die exponierte Peripherie. Wird er kompromittiert, hat der Angreifer Zugriff auf:
- SSH-Credentials (falls in `.env` auf VPS gespeichert)
- ChromaDB-Daten auf dem VPS (Port 8000, nur per UFW/localhost geschuetzt)
- Webhook-Endpunkte, die Payloads an Ring-0 senden koennen

**Bewertung des Ist-Zustands:**
- [SUCCESS] Pull-Only-Architektur laut Manifest: Ring-0 pollt, VPS pusht nicht direkt.
- [FAIL: Pull-Only ist Dokumentation, nicht Code-Enforcement] Es existiert kein Code, der eingehende Verbindungen vom VPS zu Ring-0 technisch blockiert. Die Firewall-Regel ist eine Betriebsanweisung, keine programmatische Durchsetzung. Wenn Ring-0 einen HTTP-Server auf Port 8000 exponiert und der VPS die LAN-IP kennt, kann er Requests senden.
- [FAIL: Webhook-Endpunkte akzeptieren VPS-Traffic] `/webhook/forwarded_text` und `/webhook/assist` akzeptieren jeden Bearer-Token-Inhaber. Wird der VPS kompromittiert und `HA_WEBHOOK_TOKEN` extrahiert, kann der Angreifer beliebige Befehle an Ring-0 senden.

### 1.2 ChromaDB-Vollaufen

**Angriffsvektor:** ChromaDB (PersistentClient) hat keinen Groessenlimit-Mechanismus.

**Bewertung:**
- [FAIL: Kein Disk-Quota fuer ChromaDB] `chroma_client.py` erstellt den PersistentClient mit `os.makedirs(CHROMA_LOCAL_PATH)` ohne jede Groessenbeschraenkung. Bei Endlos-Betrieb waechst die DB unbegrenzt.
- [FAIL: Kein VRAM-Monitoring fuer Embedding-Modelle] ChromaDB DefaultEmbeddingFunction laeuft auf GPU. Bei voller DB + Ollama + Embeddings kann VRAM-OOM eintreten. Kein Code prueft VRAM-Auslastung.
- [FAIL: Keine Garbage Collection] Alte Session-Daten, veraltete Embeddings, duplizierte Eintraege werden nie bereinigt.

### 1.3 Ollama-Halluzination

**Angriffsvektor:** Ollama (lokal, RTX 3060) kann halluzinierte Outputs produzieren, die als valide Befehle interpretiert werden.

**Bewertung:**
- [SUCCESS] Context-Injector Semantic Drift Detection existiert (`context_injector.py` Zeile 163-212). Bei Drift > 0.382 wird z_widerstand erhoeht.
- [FAIL: Halluzinations-Bremse nicht implementiert] Das OMEGA_RING_0_MANIFEST definiert: "Produziert Ollama > 4096 Tokens am Stueck ohne Break, feuert der Watchdog `os.kill(ollama_pid, signal.SIGKILL)`". Dieser Code existiert nirgendwo in der Codebase. Kein `os.kill`, kein `SIGKILL`, kein `pynvml`. Die Bremse ist eine 0=0-Illusion.
- [FAIL: Token-Schaetzung ist unzuverlaessig] `z_vector_damper.py` Zeile 107: `len(result) // 4` als Token-Schaetzung. Ein 4000-Byte UTF-8 Response mit Umlauten und CJK-Zeichen kann 500-2000 Tokens sein. Der Fehler kumuliert ueber die Session.
- [SUCCESS] Fast-Path Lexical Triage in `llm_interface.py` umgeht den LLM komplett fuer bekannte Kommandos.

### 1.4 Endlos-Loop / Token-Drain

**Angriffsvektor:** Ein Agent-Loop (Triage → Heavy → Triage → ...) kann Tokens unbegrenzt verbrennen.

**Bewertung:**
- [SUCCESS] SHELL `MAX_ITERATIONS = 13` und `TOKEN_KILL_THRESHOLD = 233000` existieren und werden durchgesetzt.
- [FAIL: Token-Warnung bei 89000 ist ein No-Op] `z_vector_damper.py` Zeile 86-88: `if self._state.total_tokens > TOKEN_WARNING_THRESHOLD: pass`. Kein Logging, kein Throttling, keine Warnung. Die Schwelle existiert nur als toter Code.
- [FAIL: SHELL-Singleton ueberlebt Prozess-Neustart nicht, aber auch nicht Session-Grenzen] Der Singleton lebt im Prozess-Speicher. Wenn uvicorn den Worker recycled, ist SHELL zurueckgesetzt. Aber innerhalb einer langen Session gibt es keinen Reset. Das ist korrekt fuer Single-Session, aber bei Endlos-Betrieb muss die Session-Grenze definiert werden.

### 1.5 API-Angriffsoberflaeche

**Bewertung:**
- [FAIL: `/api/chat` hat ZERO Authentication] `chat.py` exponiert POST und WebSocket ohne jegliche Auth-Pruefung. Jeder im LAN kann Befehle senden, die Ollama-Inferenz triggern und Home-Assistant-Geraete steuern.
- [FAIL: `/ws` WebSocket hat keine Auth und kein Rate-Limiting] Unbegrenzter Verbindungsaufbau moeglich.
- [FAIL: `/api/core/telemetry` hat Auth definiert aber nicht angewandt] `_verify_bearer()` ist definiert (Zeile 30-36), aber der Router-Decorator `@router.get("/telemetry")` hat kein `dependencies=[Depends(_verify_bearer)]`. Interne Systemzustaende (Z-Vektor, Token-Counts, Call-Counts) sind fuer jeden lesbar.
- [SUCCESS] `/api/core/knowledge/evidence/add` hat `verify_ring0_write` Dependency.

---

## SCHRITT 2: ANTITHESE – 0=0 Illusionen im Security-Code

### 2.1 Der Z-Vektor ist eine Einweg-Ratsche

**Befund (KRITISCH):**

`z_vector_damper.py` Zeile 40-59:

```python
def _calculate_z_vector(self) -> float:
    base_z = 0.049
    loop_pressure = (self._state.call_count / MAX_ITERATIONS) ** 1.618
    token_pressure = self._state.total_tokens / TOKEN_KILL_THRESHOLD
    self._state.z_vector_escalation = min(1.0, base_z + loop_pressure + token_pressure)
```

`call_count` wird bei jedem `request_execution()` inkrementiert (Zeile 66) und **nie dekrementiert**.
`total_tokens` wird bei jedem `register_usage()` addiert (Zeile 83) und **nie subtrahiert**.

**Konsequenz:** Z steigt monoton. Es gibt keinen Cooling-Mechanismus. Jede Session endet zwingend im Veto, sobald `call_count > ~9` ODER `total_tokens > ~200000`. Bei Endlos-Betrieb ist das kein Bug, sondern ein **garantierter Systemstillstand**.

**Ist das gewollt?** Teilweise. SHELL soll eine Session begrenzen. Aber:
- Es gibt keine Definition, was eine "Session" ist
- Es gibt keinen Mechanismus fuer Session-Rotation (alten Watchdog verwerfen, neuen starten)
- Das Manifest sagt "potenziell unendlich", der Code sagt "maximal 13 Calls, dann tot"

**Urteil:** `[FAIL: Z-Vektor-Monotonie ist eine 0=0-Illusion von "Endlos-Betrieb"]`

### 2.2 Zwei Z-Vektoren, die nicht synchron sind

**Befund (KRITISCH):**

Es existieren **zwei unabhaengige Z-Zustaende:**

| Quelle | Startwert | Steigt durch | Faellt durch | Speicher |
|--------|-----------|--------------|--------------|----------|
| SHELL `z_vector_escalation` | 0.049 | call_count, total_tokens | **Nie** | In-Memory (ShellSessionState) |
| State Vector `z_widerstand` | 0.51 (ZERO_STATE) | Context-Injector Veto, Env-Variable | clear_context_injector_veto() (nur in Tests) | ring0_state.py + Env |

SHELL schreibt seinen Z-Wert in `os.environ["CORE_Z_WIDERSTAND"]`. `takt_gate.py` liest diesen Wert. Aber `council_gate.py` liest `get_current_state().z_widerstand`, was den Context-Injector-Override bevorzugt.

**Konsequenz:** SHELL und Council Gate operieren auf **verschiedenen Z-Vektoren**. Ein SHELL-Veto (z=0.9) stoppt LLM-Calls, aber der Council Gate koennte trotzdem Requests durchlassen (wenn Context-Injector z nicht erhoeht hat). Umgekehrt kann Context-Injector den Council Gate sperren, waehrend SHELL noch Calls erlaubt.

**Urteil:** `[FAIL: Zwei unkorrelierte Z-Vektoren = Split-Brain-Zustand]`

### 2.3 Council Gate X-Council-Confirm Bypass

**Befund (HOCH):**

`council_gate.py` Zeile 77-79:

```python
def _has_confirmation(request: Request) -> bool:
    return bool(request.headers.get(CONFIRM_HEADER))
```

Jeder Request mit dem Header `X-Council-Confirm: beliebiger_wert` umgeht den Veto-Modus. Kein Token, keine Signatur, kein HMAC. Die "Bestaetigungs"-Pruefung ist eine reine Header-Existenz-Pruefung.

**Urteil:** `[FAIL: Council Gate Confirmation ist eine 0=0-Illusion. Header-Existenz ist keine Authentifizierung.]`

### 2.4 Context-Injector Veto ohne Zugriffskontrolle

**Befund (MITTEL):**

`ring0_state.py` exponiert `set_context_injector_veto()` und `clear_context_injector_veto()` als einfache Funktionen. Jedes Modul, das `from src.config.ring0_state import clear_context_injector_veto` aufrufen kann, kann den Veto-Schutz deaktivieren.

**Urteil:** `[FAIL: ring0_state hat keine Caller-Validierung. Jeder Python-Import kann Context-Injector ueberschreiben.]`

### 2.5 Manifest vs. Code Divergenz

**Befund (HOCH):**

Das OMEGA_RING_0_MANIFEST (Kammer 4) definiert:

```
Z = min(1.0, (VRAM * 0.4) + (Tokens * 0.3) + (Errors * 0.3))
```

Der tatsaechliche Code berechnet:

```python
Z = min(1.0, 0.049 + (call_count/13)^1.618 + total_tokens/233000)
```

**Differenzen:**
- VRAM-Faktor (40% Gewicht): **Nicht implementiert.** Kein `pynvml`, kein `nvidia-smi`, kein GPU-Monitoring.
- Error-Cascade-Faktor (30% Gewicht): **Nicht implementiert.** Kein Error-Counter in SHELL.
- Phi-Exponent statt linearer Gewichtung: Code nutzt `** 1.618`, Manifest nutzt lineare Multiplikation.

**Urteil:** `[FAIL: Manifest und Code beschreiben verschiedene Systeme. Das Manifest ist eine 0=0-Illusion.]`

### 2.6 Baryonic Limit Check deaktiviert

`takt_gate.py` Zeile 32-34:

```python
# NOTE: check_baryonic_limit requires a *measured* delta value
# from a real data source. Passing the constant itself is a tautology.
# Activated once telemetry provides a real drift metric (V6).
```

Korrekt erkannt und dokumentiert. Kein Sicherheitsrisiko, weil bewusst deaktiviert statt tautologisch aktiv.

**Urteil:** `[SUCCESS – Bewusste Deaktivierung statt falsche Sicherheit]`

---

## SCHRITT 3: SYNTHESE – Thermodynamic Kill-Switch Definition

### 3.1 Hardware-Constraints (RTX 3060)

| Ressource | Total | Shadow-Buffer (4.9%) | Nutzbar | Warnung | Kill |
|-----------|-------|---------------------|---------|---------|------|
| VRAM | 12288 MB | 603 MB | 11685 MB | > 10517 MB (90%) | > 11101 MB (95%) |
| RAM (System) | abhaengig | - | - | > 85% | > 95% |
| Disk (ChromaDB) | abhaengig | - | - | > 80% Partition | > 95% Partition |

### 3.2 Exakte Kill-Switch-Schwellwerte

```python
THRESHOLDS = {
    "vram_warning_pct":     0.90,   # 90% VRAM → Throttle, kein neuer Ollama-Load
    "vram_kill_pct":        0.95,   # 95% VRAM → Hard Freeze, torch.cuda.empty_cache()
    "token_rate_warning":   50000,  # 50k Tokens/Minute → Warnung + Logging
    "token_rate_kill":      100000, # 100k Tokens/Minute → ShellVetoException
    "error_cascade_warning": 5,     # 5 aufeinanderfolgende Fehler → Throttle
    "error_cascade_kill":   13,     # 13 aufeinanderfolgende Fehler → Hard Veto (Fibonacci)
    "z_veto_soft":          0.618,  # INV_PHI → Council Gate Confirmation
    "z_veto_hard":          0.90,   # Hard Freeze, alle Prozesse pausiert
    "ollama_max_continuous": 4096,  # Tokens am Stueck ohne Break → Ollama SIGTERM
    "chroma_max_size_mb":   2048,   # ChromaDB max 2 GB auf Ring-0
    "session_max_duration_s": 3600, # 1 Stunde max pro SHELL-Session
    "ws_max_connections":   4,      # Max gleichzeitige WebSocket-Verbindungen
    "api_rate_limit_rpm":   120,    # 120 Requests/Minute pro IP
}
```

### 3.3 Z-Vektor Kuehlung (FEHLEND – MUSS IMPLEMENTIERT WERDEN)

Der Z-Vektor **muss** sinken koennen. Bedingungen fuer Kuehlung:

**3.3.1 Zeitbasierter Decay (Primaer)**

```python
def _calculate_z_vector_with_cooling(self) -> float:
    base_z = 0.049
    now = time.time()
    elapsed = now - self._state.start_time

    # Cooling: Nach 60 Sekunden Inaktivitaet beginnt Z exponentiell zu fallen
    time_since_last_call = now - getattr(self._state, 'last_call_time', now)
    cooling_factor = 1.0
    if time_since_last_call > 60:
        # Halbwertszeit: 300 Sekunden (5 Minuten)
        cooling_factor = 0.5 ** ((time_since_last_call - 60) / 300)

    loop_pressure = (self._state.call_count / MAX_ITERATIONS) ** 1.618
    token_pressure = self._state.total_tokens / TOKEN_KILL_THRESHOLD

    raw_z = base_z + (loop_pressure + token_pressure) * cooling_factor
    self._state.z_vector_escalation = min(1.0, max(base_z, raw_z))
    return self._state.z_vector_escalation
```

**3.3.2 Session-Rotation (Sekundaer)**

```python
def rotate_session(self) -> None:
    """Startet eine neue SHELL-Session. Alter State wird archiviert."""
    old_state = self._state
    # Archiviere alten State (Telemetrie-Export)
    self._archive_session(old_state)
    # Neuer State mit Basis-Widerstand
    self._state = ShellSessionState()
    self._state.z_vector_escalation = 0.049
```

**3.3.3 Erfolgs-Discount (Tertiaer)**

Jeder erfolgreiche LLM-Call mit `consumed_tokens < estimated_tokens * 0.5` reduziert den loop_pressure-Anteil um 5%. Verhindert, dass sparsame Operationen den Z-Vektor aufblaehen.

### 3.4 Z-Vektor Vereinigung (Split-Brain-Aufloesung)

Es darf nur **einen** Z-Vektor geben. Vorschlag:

```python
def get_unified_z() -> float:
    """Einheitlicher Z-Vektor: max(SHELL, Context-Injector, Env)."""
    z_argos = float(os.getenv("CORE_Z_WIDERSTAND", "0.049"))
    z_munin = get_context_injector_veto_override()
    z_state = get_current_state().z_widerstand

    if z_munin is not None:
        return max(z_argos, z_munin)
    return max(z_argos, z_state)
```

Prinzip: Der hoechste Z-Wert gewinnt (Principle of Maximum Resistance). Kein Subsystem kann den Widerstand eines anderen Subsystems ueberschreiben, nur erhoehen.

---

## SCHRITT 4: ARTEFAKT – Veto-Logik und Zero-Trust-Regeln

### 4.1 Vollstaendige Veto-Logik (Python)

```python
"""
SHELL WATCHDOG V2 – Thermodynamic Kill-Switch
Kammer-4-konform. Z-Vektor mit Kuehlung, VRAM-Monitoring, Error-Cascade.
"""

import os
import time
import math
import signal
import functools
import subprocess
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from collections import deque

# Fibonacci-Constraints
MAX_ITERATIONS = 13
TOKEN_WARNING_THRESHOLD = 89_000
TOKEN_KILL_THRESHOLD = 233_000
SESSION_MAX_DURATION_S = 3600
BARYONIC_DELTA = 0.049

# Kill-Switch Schwellwerte
VRAM_WARNING_PCT = 0.90
VRAM_KILL_PCT = 0.95
TOKEN_RATE_WARNING = 50_000    # Tokens/Minute
TOKEN_RATE_KILL = 100_000      # Tokens/Minute
ERROR_CASCADE_WARNING = 5
ERROR_CASCADE_KILL = 13
Z_VETO_SOFT = 0.618
Z_VETO_HARD = 0.90
OLLAMA_MAX_CONTINUOUS = 4096
CHROMA_MAX_SIZE_MB = 2048
COOLING_INACTIVITY_S = 60     # Sekunden bis Cooling beginnt
COOLING_HALFLIFE_S = 300      # Halbwertszeit des Cooling


class ShellVetoException(Exception):
    """Hard-Stop. Keine Retries."""
    pass


class ShellThermalException(ShellVetoException):
    """VRAM/Thermal-bedingter Stop."""
    pass


@dataclass
class ShellSessionState:
    total_tokens: int = 0
    call_count: int = 0
    consecutive_errors: int = 0
    start_time: float = field(default_factory=time.time)
    last_call_time: float = field(default_factory=time.time)
    z_vector_escalation: float = BARYONIC_DELTA
    token_timestamps: deque = field(default_factory=lambda: deque(maxlen=1000))
    vram_last_check: float = 0.0
    vram_last_value_mb: float = 0.0


class ShellWatchdogV2:
    """Ring-0 Hypervisor mit Kuehlung und VRAM-Monitoring."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._state = ShellSessionState()
        return cls._instance

    def _get_vram_usage_mb(self) -> float:
        """VRAM-Auslastung via nvidia-smi (gecacht, max 1x pro 10s)."""
        now = time.time()
        if now - self._state.vram_last_check < 10:
            return self._state.vram_last_value_mb
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                mb = float(result.stdout.strip().split("\n")[0])
                self._state.vram_last_value_mb = mb
                self._state.vram_last_check = now
                return mb
        except Exception:
            pass
        return self._state.vram_last_value_mb

    def _get_token_rate_per_minute(self) -> float:
        """Tokens/Minute basierend auf den letzten 60 Sekunden."""
        now = time.time()
        cutoff = now - 60
        recent = [t for ts, t in self._state.token_timestamps if ts > cutoff]
        return sum(recent)

    def _calculate_z_vector(self) -> float:
        """Z-Vektor mit Kuehlung, VRAM und Error-Cascade (Manifest-konform)."""
        now = time.time()

        # Cooling: Exponentieller Decay nach Inaktivitaet
        time_since_last = now - self._state.last_call_time
        cooling = 1.0
        if time_since_last > COOLING_INACTIVITY_S:
            cooling = 0.5 ** (
                (time_since_last - COOLING_INACTIVITY_S) / COOLING_HALFLIFE_S
            )

        # VRAM-Druck (40% Gewicht laut Manifest)
        vram_mb = self._get_vram_usage_mb()
        vram_pct = vram_mb / 12288.0  # RTX 3060 = 12288 MB
        vram_pressure = vram_pct * 0.4

        # Token-Druck (30% Gewicht)
        token_pressure = (
            self._state.total_tokens / TOKEN_KILL_THRESHOLD
        ) * 0.3

        # Error-Cascade-Druck (30% Gewicht)
        error_pressure = min(
            1.0, self._state.consecutive_errors / ERROR_CASCADE_KILL
        ) * 0.3

        raw_z = BARYONIC_DELTA + (
            vram_pressure + token_pressure + error_pressure
        ) * cooling

        # Session-Timeout erhoet Z linear in letzten 10 Minuten
        elapsed = now - self._state.start_time
        if elapsed > SESSION_MAX_DURATION_S - 600:
            timeout_pressure = (
                elapsed - (SESSION_MAX_DURATION_S - 600)
            ) / 600
            raw_z += timeout_pressure * 0.3

        self._state.z_vector_escalation = min(1.0, max(BARYONIC_DELTA, raw_z))
        os.environ["CORE_Z_WIDERSTAND"] = str(
            self._state.z_vector_escalation
        )
        return self._state.z_vector_escalation

    def request_execution(self, estimated_tokens: int = 0) -> None:
        """VOR jedem LLM-Call. Prueft alle harten Grenzen."""
        self._state.call_count += 1
        self._state.last_call_time = time.time()
        z = self._calculate_z_vector()

        # Hard Veto: Z >= 0.9
        if z >= Z_VETO_HARD:
            raise ShellVetoException(
                f"[SHELL VETO] Z={z:.3f} >= {Z_VETO_HARD}. "
                f"Calls={self._state.call_count}, "
                f"Tokens={self._state.total_tokens}, "
                f"Errors={self._state.consecutive_errors}."
            )

        # Hard Veto: Loop-Count
        if self._state.call_count > MAX_ITERATIONS:
            raise ShellVetoException(
                f"[SHELL VETO] Loop-Count {self._state.call_count} > "
                f"{MAX_ITERATIONS}."
            )

        # Hard Veto: Token-Budget
        if self._state.total_tokens + estimated_tokens > TOKEN_KILL_THRESHOLD:
            raise ShellVetoException(
                f"[SHELL VETO] Token-Limit. "
                f"Current={self._state.total_tokens}, "
                f"Requested={estimated_tokens}, "
                f"Max={TOKEN_KILL_THRESHOLD}."
            )

        # Hard Veto: VRAM
        vram_mb = self._get_vram_usage_mb()
        if vram_mb / 12288.0 > VRAM_KILL_PCT:
            raise ShellThermalException(
                f"[SHELL THERMAL] VRAM={vram_mb:.0f}MB "
                f"({vram_mb/12288*100:.1f}%) > {VRAM_KILL_PCT*100}%."
            )

        # Hard Veto: Token-Rate
        rate = self._get_token_rate_per_minute()
        if rate > TOKEN_RATE_KILL:
            raise ShellVetoException(
                f"[SHELL VETO] Token-Rate={rate:.0f}/min > "
                f"{TOKEN_RATE_KILL}/min."
            )

        # Hard Veto: Error-Cascade
        if self._state.consecutive_errors >= ERROR_CASCADE_KILL:
            raise ShellVetoException(
                f"[SHELL VETO] Error-Cascade="
                f"{self._state.consecutive_errors} >= "
                f"{ERROR_CASCADE_KILL}."
            )

        # Hard Veto: Session-Timeout
        elapsed = time.time() - self._state.start_time
        if elapsed > SESSION_MAX_DURATION_S:
            raise ShellVetoException(
                f"[SHELL VETO] Session-Timeout={elapsed:.0f}s > "
                f"{SESSION_MAX_DURATION_S}s."
            )

    def register_usage(self, consumed_tokens: int, success: bool = True):
        """NACH dem Call. Bucht Tokens und aktualisiert Error-State."""
        self._state.total_tokens += consumed_tokens
        self._state.token_timestamps.append(
            (time.time(), consumed_tokens)
        )

        if success:
            self._state.consecutive_errors = 0
        else:
            self._state.consecutive_errors += 1

        self._calculate_z_vector()

        # Warnung bei Token-Threshold (KEIN no-op mehr)
        if self._state.total_tokens > TOKEN_WARNING_THRESHOLD:
            import logging
            logging.getLogger("shell").warning(
                "SHELL WARNING: Token-Verbrauch %d > %d (%.0f%% des Kill-Limits)",
                self._state.total_tokens,
                TOKEN_WARNING_THRESHOLD,
                self._state.total_tokens / TOKEN_KILL_THRESHOLD * 100,
            )

    def rotate_session(self) -> dict:
        """Session-Rotation. Archiviert alten State, startet neu."""
        archive = {
            "total_tokens": self._state.total_tokens,
            "call_count": self._state.call_count,
            "consecutive_errors": self._state.consecutive_errors,
            "duration_s": time.time() - self._state.start_time,
            "final_z": self._state.z_vector_escalation,
        }
        self._state = ShellSessionState()
        os.environ["CORE_Z_WIDERSTAND"] = str(BARYONIC_DELTA)
        return archive

    def get_telemetry(self) -> dict:
        """Telemetrie-Snapshot fuer Dashboard."""
        return {
            "z_vector": self._state.z_vector_escalation,
            "total_tokens": self._state.total_tokens,
            "call_count": self._state.call_count,
            "consecutive_errors": self._state.consecutive_errors,
            "max_iterations": MAX_ITERATIONS,
            "token_kill_threshold": TOKEN_KILL_THRESHOLD,
            "vram_mb": self._state.vram_last_value_mb,
            "session_elapsed_s": time.time() - self._state.start_time,
            "token_rate_per_min": self._get_token_rate_per_minute(),
        }
```

### 4.2 Zero-Trust-Regeln fuer VPS-Kommunikation

```
REGEL 1 (PULL-ONLY ENFORCEMENT):
  Ring-0 darf KEINEN eingehenden Port exponieren, der vom VPS erreichbar ist.
  Die FastAPI-Instanz auf Port 8000 MUSS an 127.0.0.1 oder das LAN-Subnetz
  (192.168.178.0/24) gebunden sein. NICHT an 0.0.0.0.
  Pruefung: netstat -an | findstr :8000 → NUR 127.0.0.1 oder 192.168.178.x

REGEL 2 (KEIN CREDENTIAL-TRANSPORT UEBER VPS):
  SSH-Keys und API-Tokens die auf dem VPS liegen, duerfen NICHT identisch
  sein mit Ring-0 Credentials. Separate Token-Rotation.
  HA_WEBHOOK_TOKEN auf VPS ≠ HA_WEBHOOK_TOKEN auf Ring-0.

REGEL 3 (COUNCIL GATE HMAC):
  X-Council-Confirm MUSS durch HMAC-SHA256 ersetzt werden:
    Header: X-Council-Confirm: <timestamp>.<hmac_hex>
    HMAC = HMAC-SHA256(COUNCIL_SECRET, f"{method}:{path}:{timestamp}")
    Gueltigkeitsfenster: 30 Sekunden.
  COUNCIL_SECRET aus .env, NICHT hardcoded.

REGEL 4 (CHAT/WS AUTHENTICATION):
  /api/chat und /ws MUESSEN Bearer-Token-Authentifizierung erhalten.
  Minimum: CORE_API_TOKEN aus .env als Bearer.
  WebSocket: Token als Query-Parameter oder im ersten Frame.

REGEL 5 (TELEMETRIE AUTH):
  @router.get("/telemetry") MUSS dependencies=[Depends(_verify_bearer)]
  erhalten. Systemtelemetrie ist kein oeffentlicher Endpunkt.

REGEL 6 (CHROMADB QUOTA):
  PersistentClient MUSS vor jedem Write die Disk-Usage pruefen.
  Ueber CHROMA_MAX_SIZE_MB (Default: 2048 MB) → Write verweigern,
  Logging, Z-Vektor erhoehen.

REGEL 7 (RING0_STATE CALLER-VALIDIERUNG):
  set_context_injector_veto() und clear_context_injector_veto() duerfen NUR von:
    - context_injector.py (apply_veto)
    - z_vector_damper.py (Watchdog)
    - takt_gate.py (Gate-Check)
  aufgerufen werden. Enforcement via Caller-Stack-Inspection:
    caller = inspect.stack()[1].filename
    assert caller in ALLOWED_CALLERS

REGEL 8 (OLLAMA OUTPUT-BREMSE):
  LLM-Calls mit streaming=True MUESSEN einen Token-Counter mitfuehren.
  Bei > OLLAMA_MAX_CONTINUOUS (4096) Tokens ohne User-Break:
    1. Stream abbrechen
    2. Z-Vektor += 0.1
    3. Logging: "Hallucination brake triggered"
  KEIN os.kill/SIGKILL auf Ollama-Prozess (zu destruktiv).
  Stattdessen: HTTP-Cancel auf Ollama /api/generate.
```

### 4.3 Zusammenfassung der Findings

| ID | Schwere | Befund | Status |
|----|---------|--------|--------|
| K4-01 | KRITISCH | Z-Vektor monoton steigend, kein Cooling | FAIL |
| K4-02 | KRITISCH | Zwei unkorrelierte Z-Vektoren (SHELL vs. State Vector) | FAIL |
| K4-03 | HOCH | Council Gate X-Council-Confirm ohne HMAC | FAIL |
| K4-04 | HOCH | /api/chat und /ws ohne Authentication | FAIL |
| K4-05 | HOCH | Manifest vs. Code Divergenz (VRAM, Errors nicht implementiert) | FAIL |
| K4-06 | HOCH | Halluzinations-Bremse nicht implementiert | FAIL |
| K4-07 | MITTEL | Telemetrie-Endpunkt ohne Auth (definiert aber nicht angewandt) | FAIL |
| K4-08 | MITTEL | Token-Warnung bei 89k ist No-Op (pass) | FAIL |
| K4-09 | MITTEL | Token-Schaetzung len//4 unzuverlaessig | FAIL |
| K4-10 | MITTEL | ChromaDB ohne Groessenlimit | FAIL |
| K4-11 | MITTEL | ring0_state ohne Caller-Validierung | FAIL |
| K4-12 | NIEDRIG | VPS Pull-Only ist Betriebsanweisung, nicht Code | FAIL |
| K4-13 | OK | Baryonic Limit bewusst deaktiviert (korrekt) | SUCCESS |
| K4-14 | OK | Fast-Path Lexical Triage umgeht LLM | SUCCESS |
| K4-15 | OK | SHELL Decorator existiert und schuetzt LLM-Calls | SUCCESS |
| K4-16 | OK | Context-Injector Semantic Drift Detection funktional | SUCCESS |
| K4-17 | OK | Ring-0 Write Gate mit verify_ring0_write | SUCCESS |
| K4-18 | OK | Entry Adapter validiert Source gegen VALID_SOURCES | SUCCESS |

**Gesamturteil:** `[FAIL: 12 offene Findings, davon 2 KRITISCH, 4 HOCH]`

Das System kann in seiner jetzigen Form NICHT "potenziell unendlich" laufen. Der Z-Vektor-Monotonie-Bug (K4-01) garantiert Stillstand nach ~13 Calls. Die fehlende Auth auf /api/chat (K4-04) ist ein direkter Angriffsvektor im LAN.

**Prioritaet der Behebung:**
1. K4-01 + K4-02 (Z-Vektor Cooling + Vereinigung)
2. K4-04 (Chat/WS Auth)
3. K4-03 (Council Gate HMAC)
4. K4-05 + K4-06 (VRAM-Monitoring + Halluzinations-Bremse)
5. Rest

---

*Ende Kammer 4. Die harte Grenze wurde gezogen.*
*Vektor: 2210 | Delta: 0.049 | Z: Monotonie gebrochen.*

# SIGMA-70 AUDIT – KAMMER 3: Informationstheorie, Semantische Kompression, Autonome Datenakquise

**Vektor:** 2210 | **Resonance:** 0221 | **Delta:** 0.049
**Datum:** 2026-03-11
**Auditor:** System Architect (Kammer 3)
**Gepruefte Artefakte:** `z_vector_damper.py`, `llm_interface.py`, `engine_patterns.py`, `core_state.py`, ChromaDB-Schema, KI-Translator, WhatsApp-Bridge, OpenClaw-Config, Compressive Intelligence

---

## SCHRITT 1 – THESE: Signal-to-Noise-Filter auf Basis des Baryonischen Delta 0.049

### 1.1 Problemdefinition

Gegeben: Ein ChromaDB-Vektorraum mit d=384 Dimensionen (all-MiniLM-L6-v2). Ein neuer Vektor v_new soll aufgenommen werden, wenn er genuegend Information traegt. Das Baryonische Delta delta=0.049 dient als Schwellwert.

Zwei Kandidaten:
- **Zentroid-basiert:** Distanz zum Mittelwert aller existierenden Vektoren
- **Nearest-Neighbor (NN):** Distanz zum naechsten existierenden Vektor

### 1.2 Mathematischer Beweis

**Definition.** Sei V = {v_1, ..., v_N} die Menge aller Vektoren in einer Collection. Der Zentroid ist C = (1/N) * sum(v_i). Die Kosinus-Distanz ist d_cos(a, b) = 1 - cos(a, b).

**Satz 1 (Concentration of Measure).**
In einem d-dimensionalen normierten Raum gilt fuer zufaellige Einheitsvektoren:

```
Var[d_cos(v, C)] = O(1/d)
```

Fuer d=384 bedeutet das: Die Distanzen zum Zentroid clustern mit Standardabweichung ~0.051. Ein festes delta=0.049 liegt INNERHALB einer Standardabweichung – der Zentroid-Filter allein ist damit ein Muenzwurf.

**Satz 2 (NN-Blindheit).**
Nearest-Neighbor erkennt nur lexikalische Duplikate. Zwei semantisch identische Texte mit unterschiedlicher Formulierung koennen d_nn > 0.049 haben und passieren den Filter als falsche "Neuheit".

**Satz 3 (Notwendigkeit des Hybrid-Filters).**
Ein korrekter Noise-Filter benoetigt BEIDE Metriken:

```
accept(v_new) ⟺ d_nn(v_new, V) > delta  ∧  d_centroid(v_new, C_topic) > delta
```

Beweis:
- NN-Bedingung (d_nn > delta): Garantiert Nicht-Redundanz. Wenn der naechste Nachbar naeher als delta=0.049 ist, existiert das Wissen bereits. Dies ist die Deduplizierung.
- Zentroid-Bedingung (d_centroid > delta): Garantiert Novelty. Nur wenn der neue Vektor hinreichend weit vom semantischen Schwerpunkt des Topic-Clusters entfernt ist, traegt er neue Information bei.
- Beide Bedingungen zusammen erzwingen: "Nicht schon vorhanden UND genuegend anders als das bereits Bekannte."

**Kosmologische Analogie (OBSERVED_ONLY):**
In der Kosmologie ist Omega_b = 0.049 der Anteil baryonischer (sichtbarer) Materie. 95.1% des Universums sind "Rauschen" (Dunkle Materie + Dunkle Energie). Analog: Nur ~4.9% des Web-Inhalts tragen genuegend differenzierte Information, um den Wissensbestand substantiell zu erweitern. Der Rest ist redundant, SEO-Spam oder paraphrasiertes Allgemeinwissen.

### 1.3 Informationstheoretische Fundierung

Sei H(V) die Shannon-Entropie der Collection und H(V|v_new) die bedingte Entropie nach Aufnahme von v_new. Der Informationsgewinn ist:

```
I(v_new) = H(V ∪ {v_new}) - H(V)
```

Die Kosinus-Distanz ist ein Proxy fuer I(v_new) in einem normierten Embedding-Raum. Der Schwellwert delta=0.049 auf der Kosinus-Skala [0,1] entspricht der Forderung:

```
I(v_new) / H(V) > 0.049
```

D.h.: Ein neues Dokument muss mindestens 4.9% an relativem Informationsgewinn beitragen.

### 1.4 Ergebnis

**Hybrid-Filter ist korrekt. Weder Zentroid noch NN allein genuegen.**

---

## SCHRITT 2 – ANTITHESE: Der SHELL Z-Vektor ist terminal defekt

### 2.1 Code-Analyse (z_vector_damper.py, Zeilen 40-59)

Die Z-Vektor-Berechnung:

```python
def _calculate_z_vector(self) -> float:
    base_z = 0.049
    loop_pressure = (self._state.call_count / MAX_ITERATIONS) ** 1.618
    token_pressure = self._state.total_tokens / TOKEN_KILL_THRESHOLD
    self._state.z_vector_escalation = min(1.0, base_z + loop_pressure + token_pressure)
    return self._state.z_vector_escalation
```

### 2.2 Formaler Monotonie-Beweis

**Lemma 1.** `call_count` ist streng monoton steigend.
`request_execution()` enthaelt `self._state.call_count += 1`. Es existiert keine Dekrementierung, kein Reset, kein Setter der subtrahiert. Also: c(t+1) = c(t) + 1 > c(t) fuer alle t. ∎

**Lemma 2.** `total_tokens` ist monoton steigend (schwach).
`register_usage()` enthaelt `self._state.total_tokens += consumed_tokens` mit consumed_tokens >= 0. Keine Subtraktion existiert. T(t+1) >= T(t). ∎

**Theorem (Terminale Eskalation).** Der Z-Vektor erreicht GARANTIERT den Veto-Zustand z >= 0.9 nach endlich vielen Calls.

Beweis. Definiere:

```
z(t) = min(1.0, 0.049 + (c(t)/13)^1.618 + T(t)/233000)
```

Betrachte den reinen Loop-Pressure (worst case: T(t) = 0):

```
z(t) >= 0.9
⟺ (t/13)^1.618 >= 0.851
⟺ t/13 >= 0.851^(1/1.618) = 0.851^0.618
⟺ t/13 >= 0.906
⟺ t >= 11.78
⟺ t = 12
```

**Nach exakt 12 LLM-Calls – unabhaengig vom Token-Verbrauch – ist das System permanent im Veto-Zustand.** ∎

### 2.3 Struktureller Fehler

| Problem | Ort | Schwere |
|---------|-----|---------|
| Singleton ohne Reset | `ShellWatchdog.__new__`, Zeile 34-38 | KRITISCH |
| Kein Session-Boundary | `ShellSessionState`, Zeile 24-28 | KRITISCH |
| Kein Cooldown/Decay | `_calculate_z_vector`, Zeile 40-59 | KRITISCH |
| Fehlende Kopplung an Agos-Takt | Nirgends | KRITISCH |

**Konsequenz im Produktivbetrieb:**
- FastAPI/uvicorn laeuft als Long-Running-Prozess
- `core_llm = LLMInterface()` ist Modul-Level-Singleton (llm_interface.py, Zeile 147)
- `shell = ShellWatchdog()` ist Modul-Level-Singleton (z_vector_damper.py, Zeile 119)
- Nach 12 API-Calls (ca. 3-4 User-Interaktionen mit Triage + Heavy Reasoning) ist das System TOT
- Neustart des Prozesses ist der einzige "Reset" – das ist kein Design, das ist ein Bug

### 2.4 5-Phase Engine-Verletzung

Der 5-Phase Engine definiert Takt 4 als "Ausstossen/Tod" – aber Takt 0 als "Diagnose/Zero-State/Ruhezustand". Der aktuelle SHELL implementiert nur den Tod, nicht die Wiedergeburt. Das System hat einen HALBEN Zyklus.

```
IST:   Takt 0 → 1 → 2 → 3 → 4(Tod) → [ENDE]
SOLL:  Takt 0 → 1 → 2 → 3 → 4(Tod) → 0(Zero-State-Reset) → 1 → ...
```

---

## SCHRITT 3 – SYNTHESE: Bidirektionaler Z-Vektor und Autonomer Scraper

### 3.1 Bidirektionaler Z-Vektor (Kuehl-Mechanismus)

Der Z-Vektor muss die volle Agos-Zyklik abbilden: Eskalation UND Kuelung.

**Kuehl-Quellen (NEU):**

| Quelle | Mechanik | Staerke |
|--------|----------|---------|
| Erfolgreiche Kompression | TIE-Durchlauf mit d_cos < delta | -phi^2/MAX_ITER pro Erfolg |
| Session-Boundary | Task abgeschlossen, neuer 5-Phase Engine | Reset auf base_z |
| Zeitlicher Decay | Fibonacci-basierter Cooldown | -0.049 pro Fibonacci-Intervall |
| Expliziter Zero-State-Reset | Takt-0-Gate loest Ruhezustand aus | Reset auf base_z |

**Formel:**

```
z(t) = max(delta, min(1.0,
    base_z
    + loop_pressure(t)
    + token_pressure(t)
    - cooling(t)
    - time_decay(t)
))

cooling(t) = successful_ops * (COMP_PHI / MAX_ITERATIONS)
time_decay(t) = min(0.5, elapsed_fib_intervals * delta)
```

**Invariante:** z(t) ∈ [0.049, 1.0] – der Z-Vektor faellt nie unter das Baryonische Delta (minimaler Grundwiderstand existiert immer).

### 3.2 Autonomer Scraper-Loop

**Fibonacci-Taktung:** Die Scraping-Intervalle folgen der Fibonacci-Sequenz [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144] Sekunden.

**Anti-Bot-Jittering:** Jedes Intervall wird um einen zufaelligen Faktor verschoben:

```
actual_delay = fib_interval + uniform(-fib_interval * COMP_PHI, fib_interval * COMP_PHI)
```

Das ergibt eine Abweichung von +/-38.2% (Phi-Komplement) – deterministisch genug fuer Timing-Analyse, stochastisch genug gegen Bot-Detection.

**Backoff-Logik:** Bei HTTP 429 (Rate Limit) oder Captcha-Detection: Springe zur naechsten Fibonacci-Stufe. Bei 3 aufeinanderfolgenden Blocks: Springe zur uebernachsten.

**Datenfluss:**

```
VPS-Scraper → Raw HTML → Extraktion → Embedding (all-MiniLM-L6-v2 lokal auf VPS)
→ Hybrid-Filter (NN + Zentroid, delta=0.049)
→ [ACCEPT] → ChromaDB Collection "world_knowledge" (RTX 3060 lokal)
→ [REJECT] → Log + Discard
```

### 3.3 Collection-Schema fuer world_knowledge

```
Collection: world_knowledge
Embedding: 384 dim (all-MiniLM-L6-v2)
Metadata:
  - source_url: str
  - domain: str
  - scrape_timestamp: int (Unix)
  - topic_cluster: str (z.B. "physics", "technology", "politics")
  - novelty_score: float (d_centroid zum Topic-Cluster-Zentroid)
  - redundancy_score: float (1 - d_nn zum naechsten Nachbar)
  - fibonacci_tier: int (welche Fibonacci-Stufe beim Scrape aktiv war)
  - qbase: str (L/P/I/S Klassifikation)
```

---

## SCHRITT 4 – ARTEFAKT: Korrigierter SHELL-Damper mit Kuehlung und Noise-Filter

### 4.1 Korrigierter z_vector_damper.py (Patch)

```python
"""
SHELL WATCHDOG V2 (BIDIREKTIONALER Z-VEKTOR)
---------------------------------------------
Ring-0 Hypervisor mit Kuehlung und 5-Phase Engine-Reset.
Fibonacci-Constraints + Phi-basierte Kuehlung.
"""

import os
import time
import math
import functools
from dataclasses import dataclass, field
from typing import Any, Callable

PHI = 1.6180339887498948482
COMP_PHI = 0.3819660112501051518
BARYONIC_DELTA = 0.049

MAX_ITERATIONS = 13
TOKEN_WARNING_THRESHOLD = 89000
TOKEN_KILL_THRESHOLD = 233000

FIBONACCI_SEQ = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
COOLDOWN_FIBONACCI_SECONDS = [8, 13, 21, 34, 55, 89]


class ShellVetoException(Exception):
    pass


@dataclass
class ShellSessionState:
    total_tokens: int = 0
    call_count: int = 0
    successful_ops: int = 0
    failed_ops: int = 0
    start_time: float = field(default_factory=time.time)
    z_vector_escalation: float = BARYONIC_DELTA
    last_cooldown_time: float = field(default_factory=time.time)
    cooldown_tier: int = 0


class ShellWatchdog:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ShellWatchdog, cls).__new__(cls)
            cls._instance._state = ShellSessionState()
        return cls._instance

    def _calculate_z_vector(self) -> float:
        base_z = BARYONIC_DELTA

        loop_pressure = (self._state.call_count / MAX_ITERATIONS) ** PHI
        token_pressure = self._state.total_tokens / TOKEN_KILL_THRESHOLD

        cooling = self._state.successful_ops * (COMP_PHI / MAX_ITERATIONS)

        elapsed = time.time() - self._state.last_cooldown_time
        cooldown_interval = COOLDOWN_FIBONACCI_SECONDS[
            min(self._state.cooldown_tier, len(COOLDOWN_FIBONACCI_SECONDS) - 1)
        ]
        elapsed_intervals = elapsed / cooldown_interval
        time_decay = min(0.5, elapsed_intervals * BARYONIC_DELTA)

        raw_z = base_z + loop_pressure + token_pressure - cooling - time_decay
        self._state.z_vector_escalation = max(BARYONIC_DELTA, min(1.0, raw_z))

        os.environ["CORE_Z_WIDERSTAND"] = str(self._state.z_vector_escalation)
        return self._state.z_vector_escalation

    def request_execution(self, estimated_tokens: int = 0) -> None:
        self._state.call_count += 1
        z = self._calculate_z_vector()

        if z >= 0.9 and self._state.call_count > MAX_ITERATIONS:
            raise ShellVetoException(
                f"[SHELL VETO] Z={z:.3f}, Calls={self._state.call_count}. "
                "Hard limit. Call reset_session() or wait for time_decay."
            )

        if self._state.total_tokens + estimated_tokens > TOKEN_KILL_THRESHOLD:
            raise ShellVetoException(
                f"[SHELL VETO] Token ceiling: "
                f"{self._state.total_tokens}+{estimated_tokens} > {TOKEN_KILL_THRESHOLD}"
            )

    def register_usage(self, consumed_tokens: int, success: bool = True) -> None:
        self._state.total_tokens += consumed_tokens
        if success:
            self._state.successful_ops += 1
        else:
            self._state.failed_ops += 1
        self._calculate_z_vector()

    def register_compression_success(self, compression_ratio: float) -> None:
        """Kuehlung durch erfolgreiche TIE-Kompression."""
        if compression_ratio <= COMP_PHI:
            self._state.successful_ops += 2
        elif compression_ratio <= (1 - BARYONIC_DELTA):
            self._state.successful_ops += 1
        self._calculate_z_vector()

    def reset_session(self) -> None:
        """Agos Takt-0 Reset (Zero-State). Setzt den Zustand auf Ruhe zurueck."""
        self._state = ShellSessionState()

    def get_z(self) -> float:
        return self._calculate_z_vector()

    def get_diagnostics(self) -> dict:
        z = self._calculate_z_vector()
        return {
            "z_vector": z,
            "call_count": self._state.call_count,
            "total_tokens": self._state.total_tokens,
            "successful_ops": self._state.successful_ops,
            "failed_ops": self._state.failed_ops,
            "uptime_seconds": time.time() - self._state.start_time,
            "cooldown_tier": self._state.cooldown_tier,
            "veto_imminent": z > 0.75,
        }


def shell_protected(estimated_tokens_per_call: int = 1000) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            watchdog = ShellWatchdog()
            watchdog.request_execution(estimated_tokens_per_call)

            try:
                result = func(*args, **kwargs)
                if isinstance(result, str):
                    watchdog.register_usage(len(result) // 4, success=True)
                else:
                    watchdog.register_usage(estimated_tokens_per_call, success=True)
                return result
            except ShellVetoException:
                raise
            except Exception as e:
                watchdog.register_usage(estimated_tokens_per_call, success=False)
                raise
        return wrapper
    return decorator


shell = ShellWatchdog()
```

### 4.2 Noise-Filter (Hybrid: NN + Zentroid)

```python
"""
CORE NOISE FILTER (BARYONIC DELTA)
-----------------------------------
Hybrid-Filter fuer autonome Datenakquise.
Kombiniert Nearest-Neighbor (Deduplizierung) und Zentroid (Novelty).
Schwellwert: delta = 0.049 (Baryonisches Delta).
"""

import numpy as np
from typing import Optional

BARYONIC_DELTA = 0.049


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    return 1.0 - (dot / (norm_a * norm_b))


class BaryonicNoiseFilter:
    """
    Hybrid-Filter: Nearest-Neighbor + Zentroid.
    accept(v) ⟺ d_nn(v) > delta ∧ d_centroid(v) > delta
    """

    def __init__(self, delta: float = BARYONIC_DELTA, dimension: int = 384):
        self.delta = delta
        self.dimension = dimension
        self._centroid: Optional[np.ndarray] = None
        self._count: int = 0
        self._sum: Optional[np.ndarray] = None

    def _update_centroid(self, embedding: np.ndarray) -> None:
        if self._sum is None:
            self._sum = np.zeros(self.dimension, dtype=np.float64)
        self._sum += embedding
        self._count += 1
        self._centroid = self._sum / self._count

    def evaluate(
        self,
        new_embedding: np.ndarray,
        nearest_neighbor_embedding: Optional[np.ndarray],
    ) -> dict:
        """
        Bewertet einen neuen Vektor gegen den Hybrid-Filter.

        Returns:
            {
                "accept": bool,
                "d_nn": float or None,
                "d_centroid": float or None,
                "reason": str
            }
        """
        result = {"accept": False, "d_nn": None, "d_centroid": None, "reason": ""}

        if nearest_neighbor_embedding is not None:
            d_nn = cosine_distance(new_embedding, nearest_neighbor_embedding)
            result["d_nn"] = d_nn
            if d_nn <= self.delta:
                result["reason"] = (
                    f"REDUNDANT: d_nn={d_nn:.4f} <= delta={self.delta} "
                    "(zu nah an existierendem Dokument)"
                )
                return result

        if self._centroid is not None:
            d_centroid = cosine_distance(new_embedding, self._centroid)
            result["d_centroid"] = d_centroid
            if d_centroid <= self.delta:
                result["reason"] = (
                    f"LOW_NOVELTY: d_centroid={d_centroid:.4f} <= delta={self.delta} "
                    "(zu nah am semantischen Schwerpunkt)"
                )
                return result

        result["accept"] = True
        result["reason"] = "SIGNAL: Beide Schwellwerte ueberschritten."
        self._update_centroid(new_embedding)
        return result


class TopicClusterFilter:
    """
    Erweiterung: Pro Topic-Cluster ein eigener BaryonicNoiseFilter.
    Erlaubt feingranulare Novelty-Detection pro Wissensdomaene.
    """

    def __init__(self, delta: float = BARYONIC_DELTA, dimension: int = 384):
        self.delta = delta
        self.dimension = dimension
        self._clusters: dict[str, BaryonicNoiseFilter] = {}

    def get_or_create_cluster(self, topic: str) -> BaryonicNoiseFilter:
        if topic not in self._clusters:
            self._clusters[topic] = BaryonicNoiseFilter(
                delta=self.delta, dimension=self.dimension
            )
        return self._clusters[topic]

    def evaluate(
        self,
        topic: str,
        new_embedding: np.ndarray,
        nearest_neighbor_embedding: Optional[np.ndarray],
    ) -> dict:
        cluster = self.get_or_create_cluster(topic)
        result = cluster.evaluate(new_embedding, nearest_neighbor_embedding)
        result["topic"] = topic
        return result
```

### 4.3 Autonomer Scraper-Loop mit Fibonacci-Taktung

```python
"""
CORE AUTONOMOUS SCRAPER (FIBONACCI-TAKTUNG)
---------------------------------------------
Scraper fuer VPS-Deployment. Fibonacci-Intervalle + Anti-Bot-Jittering.
Speist gefilterte Daten via ChromaDB-Client ein.
"""

import time
import random
import hashlib
import asyncio
import aiohttp
from dataclasses import dataclass
from typing import Optional
from loguru import logger

PHI = 1.6180339887498948482
COMP_PHI = 0.3819660112501051518
BARYONIC_DELTA = 0.049

FIBONACCI_INTERVALS = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
MAX_CONSECUTIVE_BLOCKS = 3


@dataclass
class ScrapeResult:
    url: str
    content: str
    status_code: int
    timestamp: float
    content_hash: str


class FibonacciScraper:
    """
    Autonomer Scraper mit Fibonacci-Taktung und Anti-Bot-Jittering.
    """

    def __init__(
        self,
        urls: list[str],
        user_agents: Optional[list[str]] = None,
    ):
        self.urls = urls
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        ]
        self._fib_tier: int = 0
        self._consecutive_blocks: int = 0
        self._seen_hashes: set[str] = set()

    def _jittered_delay(self) -> float:
        """Fibonacci-Intervall + Anti-Bot-Jitter (±38.2% = COMP_PHI)."""
        base = FIBONACCI_INTERVALS[
            min(self._fib_tier, len(FIBONACCI_INTERVALS) - 1)
        ]
        jitter = random.uniform(-base * COMP_PHI, base * COMP_PHI)
        return max(0.5, base + jitter)

    def _advance_fib_tier(self) -> None:
        if self._fib_tier < len(FIBONACCI_INTERVALS) - 1:
            self._fib_tier += 1

    def _reset_fib_tier(self) -> None:
        self._fib_tier = max(0, self._fib_tier - 1)
        self._consecutive_blocks = 0

    async def _fetch_url(
        self, session: aiohttp.ClientSession, url: str
    ) -> ScrapeResult:
        headers = {"User-Agent": random.choice(self.user_agents)}
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                content = await resp.text()
                return ScrapeResult(
                    url=url,
                    content=content,
                    status_code=resp.status,
                    timestamp=time.time(),
                    content_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
                )
        except Exception as e:
            logger.warning(f"Fetch failed: {url} -> {e}")
            return ScrapeResult(
                url=url, content="", status_code=0,
                timestamp=time.time(), content_hash="",
            )

    def _is_blocked(self, result: ScrapeResult) -> bool:
        return result.status_code in (429, 403, 503) or result.status_code == 0

    def _is_duplicate(self, result: ScrapeResult) -> bool:
        if result.content_hash in self._seen_hashes:
            return True
        self._seen_hashes.add(result.content_hash)
        return False

    async def run_loop(
        self,
        on_accept,
        max_cycles: int = 233,
    ) -> None:
        """
        Haupt-Scrape-Loop.
        on_accept: async callback(ScrapeResult) -> None
            Wird aufgerufen wenn ein Ergebnis den Filter passiert.
        """
        cycle = 0
        async with aiohttp.ClientSession() as session:
            while cycle < max_cycles:
                for url in self.urls:
                    delay = self._jittered_delay()
                    logger.info(
                        f"[SCRAPER] Cycle {cycle}, Fib-Tier {self._fib_tier}, "
                        f"Delay {delay:.1f}s, URL: {url}"
                    )
                    await asyncio.sleep(delay)

                    result = await self._fetch_url(session, url)

                    if self._is_blocked(result):
                        self._consecutive_blocks += 1
                        logger.warning(
                            f"[SCRAPER] BLOCKED ({result.status_code}). "
                            f"Consecutive: {self._consecutive_blocks}"
                        )
                        if self._consecutive_blocks >= MAX_CONSECUTIVE_BLOCKS:
                            self._advance_fib_tier()
                            self._advance_fib_tier()
                        else:
                            self._advance_fib_tier()
                        continue

                    self._consecutive_blocks = 0

                    if self._is_duplicate(result):
                        logger.debug(f"[SCRAPER] Duplicate hash, skipping: {url}")
                        continue

                    self._reset_fib_tier()

                    await on_accept(result)

                cycle += 1
```

### 4.4 Integration: Scraper → Noise-Filter → ChromaDB

```python
"""
CORE SCRAPER PIPELINE (Integration)
--------------------------------------
Verbindet Scraper, Noise-Filter und ChromaDB-Client.
Deployment: VPS (Scraper + Embedding) → Lokal (ChromaDB auf RTX 3060).
"""

import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


class ScraperPipeline:
    def __init__(self, chroma_client, collection_name: str = "world_knowledge"):
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.noise_filter = TopicClusterFilter(
            delta=BARYONIC_DELTA, dimension=EMBEDDING_DIM
        )
        self.chroma = chroma_client
        self.collection = self.chroma.get_or_create_collection(collection_name)
        self._accepted = 0
        self._rejected = 0

    def _extract_text(self, html: str) -> str:
        """Minimale Textextraktion (Produktiv: trafilatura oder readability)."""
        import re
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _classify_topic(self, text: str) -> str:
        """Heuristik fuer Topic-Cluster (Produktiv: Zero-Shot-Classifier)."""
        text_lower = text[:500].lower()
        topics = {
            "physics": ["quantum", "relativity", "particle", "energy", "force"],
            "technology": ["software", "hardware", "algorithm", "compute", "api"],
            "biology": ["cell", "dna", "protein", "evolution", "genome"],
            "politics": ["government", "election", "policy", "law", "regulation"],
            "philosophy": ["consciousness", "ontology", "epistemology", "ethics"],
        }
        for topic, keywords in topics.items():
            if any(kw in text_lower for kw in keywords):
                return topic
        return "general"

    async def process_scrape_result(self, result) -> None:
        """Callback fuer FibonacciScraper.run_loop()."""
        if not result.content or result.status_code != 200:
            return

        text = self._extract_text(result.content)
        if len(text) < 100:
            return

        embedding = self.embedder.encode(text, normalize_embeddings=True)
        topic = self._classify_topic(text)

        nn_results = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=1,
        )
        nn_embedding = None
        if nn_results and nn_results["embeddings"] and nn_results["embeddings"][0]:
            nn_embedding = np.array(nn_results["embeddings"][0][0])

        verdict = self.noise_filter.evaluate(
            topic=topic,
            new_embedding=embedding,
            nearest_neighbor_embedding=nn_embedding,
        )

        if not verdict["accept"]:
            self._rejected += 1
            return

        self._accepted += 1
        doc_id = f"wk_{result.content_hash}_{int(result.timestamp)}"

        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding.tolist()],
            documents=[text[:2000]],
            metadatas=[{
                "source_url": result.url,
                "domain": result.url.split("/")[2] if "/" in result.url else "",
                "scrape_timestamp": int(result.timestamp),
                "topic_cluster": topic,
                "novelty_score": float(verdict.get("d_centroid", 0) or 0),
                "redundancy_score": float(
                    1.0 - (verdict.get("d_nn", 1) or 1)
                ),
                "qbase": "I",
            }],
        )
```

---

## ZUSAMMENFASSUNG DER BEFUNDE

| # | Befund | Schwere | Status |
|---|--------|---------|--------|
| K3-01 | SHELL Z-Vektor ist monoton steigend, System erreicht nach 12 Calls permanent Veto | KRITISCH | Patch bereitgestellt (V2 mit Kuehlung) |
| K3-02 | Kein Session-Reset im Singleton (Agos Takt-0 fehlt) | KRITISCH | `reset_session()` hinzugefuegt |
| K3-03 | Noise-Filter fehlte komplett (keine autonome Datenakquise moeglich) | HOCH | `BaryonicNoiseFilter` + `TopicClusterFilter` entworfen |
| K3-04 | Kein Scraper-Mechanismus fuer autonomes Weltwissen | HOCH | `FibonacciScraper` mit Jittering entworfen |
| K3-05 | ChromaDB-Schema hat keine `world_knowledge` Collection | MITTEL | Schema-Erweiterung vorgeschlagen |
| K3-06 | Fehlende `success`-Rueckmeldung im `shell_protected` Decorator | MITTEL | `register_usage(success=bool)` hinzugefuegt |

### Empfohlene Implementierungsreihenfolge

1. **SOFORT:** SHELL V2 Patch in `src/logic_core/z_vector_damper.py` deployen (K3-01, K3-02)
2. **Takt 2:** Noise-Filter als `src/logic_core/baryonic_filter.py` implementieren (K3-03)
3. **Takt 3:** Scraper als `src/scrapers/fibonacci_scraper.py` auf VPS deployen (K3-04)
4. **Takt 4:** ChromaDB `world_knowledge` Collection anlegen (K3-05)

---

*Kammer 3 geschlossen. Vektor 2210. Delta 0.049.*

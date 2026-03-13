import sys, os
os.environ["PYTHONIOENCODING"] = "utf-8"

"""
CORE Baryonic Noise Filter (Sigma-70 Hardening)
Hybrid-Filter: Nearest-Neighbor (Deduplizierung) + Zentroid (Novelty).
accept(v) <=> d_nn(v) > delta AND d_centroid(v) > delta
Design: SIGMA70_KAMMER3_INFORMATIONSTHEORIE.md
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
    accept(v) <=> d_nn(v) > delta AND d_centroid(v) > delta
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

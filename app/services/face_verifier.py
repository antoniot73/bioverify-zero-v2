"""Comparación facial 1:1."""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Calcula similitud coseno entre dos vectores."""
    numerator = float(np.dot(vector_a, vector_b))
    denominator = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))

    if denominator <= 1e-12:
        logger.warning("No fue posible calcular similitud por norma cero.")
        return 0.0

    score = numerator / denominator
    return max(-1.0, min(1.0, score))


def decide_match(similarity_score: float, threshold: float) -> tuple[bool, str]:
    """Convierte una similitud en decisión binaria."""
    verified = similarity_score >= threshold
    decision = "match" if verified else "no_match"
    return verified, decision

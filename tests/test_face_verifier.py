"""Pruebas de similitud facial."""

from __future__ import annotations

import numpy as np

from app.services.face_verifier import cosine_similarity, decide_match


def test_cosine_similarity_identical_vectors() -> None:
    """Dos vectores idénticos deben producir similitud 1."""
    vector = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    score = cosine_similarity(vector, vector)

    assert round(score, 6) == 1.0


def test_decide_match() -> None:
    """Valida decisión por umbral."""
    verified, decision = decide_match(0.95, 0.90)

    assert verified is True
    assert decision == "match"

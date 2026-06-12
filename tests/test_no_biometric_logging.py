"""Prueba documental de política de no logging biométrico."""

from __future__ import annotations

from pathlib import Path


def test_readme_declares_no_biometric_logging() -> None:
    """Verifica que la política esté declarada."""
    readme = Path("README.md").read_text(encoding="utf-8")

    assert "Logs estructurados sin imágenes" in readme
    assert "embeddings" in readme

"""Rutas de salud."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Reporta disponibilidad básica del servicio."""
    return {"status": "ok", "service": "bioverify-zero"}

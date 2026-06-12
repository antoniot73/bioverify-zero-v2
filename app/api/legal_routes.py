"""Rutas para documentos legales estáticos."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Response

router = APIRouter()
LEGAL_DIR = Path(__file__).resolve().parents[1] / "legal"


def _read_legal_file(filename: str) -> str:
    """Lee un documento legal del paquete."""
    return (LEGAL_DIR / filename).read_text(encoding="utf-8")


@router.get("/legal/privacy")
def privacy_notice() -> Response:
    """Devuelve el aviso de privacidad simplificado."""
    return Response(content=_read_legal_file("privacy_notice.md"), media_type="text/markdown")


@router.get("/legal/restricted-use")
def restricted_use() -> Response:
    """Devuelve la política de uso restringido."""
    return Response(content=_read_legal_file("restricted_use.md"), media_type="text/markdown")


@router.get("/legal/consent")
def consent_text() -> Response:
    """Devuelve el texto de consentimiento."""
    return Response(content=_read_legal_file("consent_text.md"), media_type="text/markdown")

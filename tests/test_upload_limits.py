"""Pruebas de controles de carga."""

from __future__ import annotations

import base64

import pytest
from fastapi import HTTPException

from app.services.image_validation import decode_base64_image


def test_invalid_base64_is_rejected() -> None:
    """Valida rechazo de Base64 inválido."""
    with pytest.raises(HTTPException):
        decode_base64_image("no-es-base64", "document_image_b64")


def test_invalid_magic_is_rejected() -> None:
    """Valida rechazo de contenido no imagen."""
    payload = base64.b64encode(b"not-an-image").decode("ascii")

    with pytest.raises(HTTPException):
        decode_base64_image(payload, "document_image_b64")

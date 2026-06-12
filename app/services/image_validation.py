"""Validación de imágenes codificadas en Base64."""

from __future__ import annotations

import base64
import binascii
import logging
import re
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)

_DATA_URL_PATTERN = re.compile(r"^data:(?P<mime>[-\w.]+/[-\w+.]+);base64,(?P<data>.+)$", re.DOTALL)


@dataclass(frozen=True)
class ImageBytes:
    """Contenedor seguro para bytes de imagen validados."""

    data: bytes
    mime: str


def _detect_mime_from_magic(data: bytes) -> str:
    """Detecta MIME real por firma básica de archivo."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"


def _strip_data_url(image_b64: str) -> tuple[str | None, str]:
    """Extrae MIME declarado y contenido Base64."""
    match = _DATA_URL_PATTERN.match(image_b64.strip())
    if match:
        return match.group("mime").lower(), match.group("data")
    return None, image_b64.strip()


def decode_base64_image(image_b64: str, field_name: str) -> ImageBytes:
    """Decodifica y valida una imagen Base64."""
    declared_mime, payload = _strip_data_url(image_b64)

    estimated_bytes = (len(payload) * 3) // 4
    if estimated_bytes > settings.max_image_bytes:
        logger.warning("Imagen rechazada por tamaño estimado excesivo en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"La imagen {field_name} excede el tamaño máximo permitido.",
        )

    try:
        image_bytes = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        logger.warning("Imagen Base64 inválida en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La imagen {field_name} no es Base64 válido.",
        ) from exc

    if len(image_bytes) > settings.max_image_bytes:
        logger.warning("Imagen rechazada por tamaño real excesivo en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"La imagen {field_name} excede el tamaño máximo permitido.",
        )

    detected_mime = _detect_mime_from_magic(image_bytes)
    if detected_mime not in {"image/jpeg", "image/png", "image/webp"}:
        logger.warning("Imagen rechazada por firma inválida en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"La imagen {field_name} no tiene un formato permitido.",
        )

    if declared_mime is not None and declared_mime != detected_mime:
        logger.warning("Imagen rechazada por discrepancia MIME en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"La imagen {field_name} tiene una discrepancia de tipo MIME.",
        )

    return ImageBytes(data=image_bytes, mime=detected_mime)

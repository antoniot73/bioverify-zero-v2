"""Controles de seguridad para solicitudes de imágenes."""

from __future__ import annotations

import logging

from fastapi import HTTPException, Request, status

from app.config import settings

logger = logging.getLogger(__name__)


def enforce_content_length(request: Request) -> None:
    """Valida el tamaño total de la solicitud antes de procesarla."""
    raw_length = request.headers.get("content-length")

    if raw_length is None:
        logger.warning("Solicitud rechazada por ausencia de Content-Length.")
        raise HTTPException(
            status_code=status.HTTP_411_LENGTH_REQUIRED,
            detail="La solicitud debe incluir Content-Length.",
        )

    try:
        content_length = int(raw_length)
    except ValueError as exc:
        logger.warning("Solicitud rechazada por Content-Length inválido.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Length inválido.",
        ) from exc

    if content_length > settings.max_total_body_bytes:
        logger.warning("Solicitud rechazada por tamaño total excesivo: %s bytes.", content_length)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="La solicitud excede el tamaño máximo permitido.",
        )


def enforce_consent(consent_accepted: bool) -> None:
    """Bloquea el procesamiento si no existe consentimiento explícito."""
    if not consent_accepted:
        logger.info("Solicitud rechazada por falta de consentimiento explícito.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere consentimiento explícito para procesar las imágenes.",
        )

"""Decodificación controlada de imágenes en matrices NumPy."""

from __future__ import annotations

import logging

import cv2
import numpy as np
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)


def decode_image_matrix(image_bytes: bytes, field_name: str) -> np.ndarray:
    """Convierte bytes de imagen a matriz BGR de OpenCV."""
    buffer = np.frombuffer(image_bytes, dtype=np.uint8)

    image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    if image is None:
        logger.warning("OpenCV no pudo decodificar la imagen del campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo decodificar la imagen {field_name}.",
        )

    height, width = image.shape[:2]
    if height <= 0 or width <= 0:
        logger.warning("Imagen con dimensiones inválidas en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La imagen {field_name} tiene dimensiones inválidas.",
        )

    longest_side = max(height, width)
    if longest_side > settings.max_image_side:
        scale = settings.max_image_side / float(longest_side)
        new_width = max(1, int(width * scale))
        new_height = max(1, int(height * scale))
        image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        logger.info("Imagen %s normalizada a %sx%s.", field_name, new_width, new_height)

    return image

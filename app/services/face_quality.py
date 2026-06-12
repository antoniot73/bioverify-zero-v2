"""Controles básicos de calidad facial."""

from __future__ import annotations

import logging

import cv2
import numpy as np
from fastapi import HTTPException, status

from app.config import settings
from app.services.face_detection import FaceBox, face_area_ratio

logger = logging.getLogger(__name__)


def estimate_blur_laplacian(image_bgr: np.ndarray) -> float:
    """Calcula nitidez aproximada mediante varianza del Laplaciano."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def estimate_brightness(image_bgr: np.ndarray) -> float:
    """Calcula brillo promedio en escala de grises."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return float(gray.mean())


def validate_face_quality(
    image_bgr: np.ndarray,
    face_bgr: np.ndarray,
    face_box: FaceBox,
    field_name: str,
) -> dict[str, float | bool]:
    """Valida calidad mínima del recorte facial y devuelve métricas."""
    height, width = face_bgr.shape[:2]
    if height < 64 or width < 64:
        logger.info("Rostro demasiado pequeño en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El rostro en {field_name} es demasiado pequeño.",
        )

    area_ratio = face_area_ratio(image_bgr, face_box)
    if area_ratio < settings.min_face_area_ratio:
        logger.info(
            "Rostro con área insuficiente en %s. Ratio=%.4f",
            field_name,
            area_ratio,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El rostro en {field_name} es demasiado pequeño dentro de la imagen.",
        )

    blur_score = estimate_blur_laplacian(face_bgr)
    if blur_score < settings.min_blur_score:
        logger.info("Rostro con baja nitidez en %s. Score=%.2f", field_name, blur_score)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El rostro en {field_name} no tiene nitidez suficiente.",
        )

    brightness = estimate_brightness(face_bgr)
    brightness_ok = settings.min_brightness <= brightness <= settings.max_brightness
    if not brightness_ok:
        logger.info("Rostro con brillo fuera de rango en %s. Brillo=%.2f", field_name, brightness)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"El rostro en {field_name} no tiene iluminación suficiente.",
        )

    return {
        "face_area_ratio": round(area_ratio, 6),
        "blur_score": round(blur_score, 3),
        "brightness": round(brightness, 3),
        "brightness_ok": True,
        "sharpness_ok": True,
    }

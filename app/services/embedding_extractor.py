"""Extracción de embeddings faciales para BioVerify-Zero v2.

La v2 reemplaza el extractor demostrativo por OpenCV SFace. El embedding facial
se calcula temporalmente durante la solicitud y luego se limpia en memoria.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np

from app.config import settings
from app.services.face_detection import FaceDetection

logger = logging.getLogger(__name__)


def _l2_normalize(vector: np.ndarray) -> np.ndarray:
    """Normaliza un vector con norma L2."""
    norm = float(np.linalg.norm(vector))
    if norm <= 1e-12:
        return vector
    return vector / norm


def _create_sface_recognizer(model_path: Path):
    """Crea recognizer SFace compatible con distintas versiones de OpenCV."""
    if not model_path.exists():
        raise RuntimeError(
            "No se encontró el modelo SFace. "
            f"Ruta esperada: {model_path}. Ejecute scripts/download_models.py."
        )

    if hasattr(cv2, "FaceRecognizerSF_create"):
        return cv2.FaceRecognizerSF_create(str(model_path), "")

    if hasattr(cv2, "FaceRecognizerSF"):
        return cv2.FaceRecognizerSF.create(str(model_path), "")

    raise RuntimeError(
        "La instalación de OpenCV no expone FaceRecognizerSF. "
        "Use opencv-contrib-python-headless compatible con SFace."
    )


class SFaceEmbeddingExtractor:
    """Extractor de embeddings faciales con OpenCV SFace."""

    model_mode = "face_embedding_no_storage"

    def __init__(self) -> None:
        self._recognizer = _create_sface_recognizer(settings.sface_model_path)

    def extract(self, image_bgr: np.ndarray, detection: FaceDetection) -> np.ndarray:
        """Extrae embedding facial desde imagen completa y detección YuNet."""
        if detection.raw is None:
            # Fallback para desarrollo si se usa Haar: recorte simple.
            from app.services.face_detection import crop_face

            face_bgr = crop_face(image_bgr, detection.box)
            aligned = cv2.resize(
                face_bgr,
                (settings.normalized_face_size, settings.normalized_face_size),
                interpolation=cv2.INTER_AREA,
            )
        else:
            aligned = self._recognizer.alignCrop(image_bgr, detection.raw)

        feature = self._recognizer.feature(aligned)
        vector = np.asarray(feature, dtype=np.float32).reshape(-1)
        return _l2_normalize(vector)


class SimpleDemoEmbeddingExtractor:
    """Extractor no biométrico solo para fallback de desarrollo."""

    model_mode = "demo_non_biometric"

    def extract(self, image_bgr: np.ndarray, detection: FaceDetection) -> np.ndarray:
        """Extrae un vector simple normalizado desde un recorte facial."""
        from app.services.face_detection import crop_face

        face_bgr = crop_face(image_bgr, detection.box)
        gray = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(
            gray,
            (settings.normalized_face_size, settings.normalized_face_size),
            interpolation=cv2.INTER_AREA,
        )
        equalized = cv2.equalizeHist(resized)
        vector = equalized.astype(np.float32).reshape(-1) / 255.0
        return _l2_normalize(vector)


def create_embedding_extractor():
    """Fábrica del extractor configurado."""
    if settings.face_embedding_mode == "demo":
        logger.warning("Usando extractor demo no biométrico por configuración.")
        return SimpleDemoEmbeddingExtractor()

    try:
        return SFaceEmbeddingExtractor()
    except RuntimeError:
        if settings.app_env == "development":
            logger.exception("SFace no disponible. Usando extractor demo en desarrollo.")
            return SimpleDemoEmbeddingExtractor()
        raise

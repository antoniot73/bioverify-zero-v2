"""Detección facial para BioVerify-Zero v2.

La v2 usa YuNet cuando los modelos ONNX están disponibles. YuNet devuelve caja
facial, landmarks y score, lo que permite usar SFace para alinear y extraer
embeddings faciales 1:1.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FaceBox:
    """Caja delimitadora facial."""

    x: int
    y: int
    w: int
    h: int


@dataclass(frozen=True)
class FaceDetection:
    """Detección facial normalizada."""

    box: FaceBox
    score: float
    raw: np.ndarray | None = None
    detector_mode: str = "unknown"


def _face_area(face_box: FaceBox) -> int:
    """Calcula el área de la caja facial."""
    return int(face_box.w * face_box.h)


def _select_largest_face(faces: list[FaceDetection]) -> FaceDetection:
    """Selecciona el rostro candidato de mayor área."""
    return max(faces, key=lambda face: _face_area(face.box))


def _create_yunet_detector(model_path: Path, input_size: tuple[int, int]):
    """Crea un detector YuNet compatible con distintas versiones de OpenCV."""
    if not model_path.exists():
        raise RuntimeError(
            "No se encontró el modelo YuNet. "
            f"Ruta esperada: {model_path}. Ejecute scripts/download_models.py."
        )

    if hasattr(cv2, "FaceDetectorYN_create"):
        return cv2.FaceDetectorYN_create(
            str(model_path),
            "",
            input_size,
            settings.yunet_score_threshold,
            settings.yunet_nms_threshold,
            settings.yunet_top_k,
        )

    if hasattr(cv2, "FaceDetectorYN"):
        return cv2.FaceDetectorYN.create(
            str(model_path),
            "",
            input_size,
            settings.yunet_score_threshold,
            settings.yunet_nms_threshold,
            settings.yunet_top_k,
        )

    raise RuntimeError(
        "La instalación de OpenCV no expone FaceDetectorYN. "
        "Use opencv-contrib-python-headless compatible con YuNet."
    )


_YUNET_DETECTOR = None


def _get_yunet_detector(input_size: tuple[int, int]):
    """Inicializa una única instancia de YuNet y ajusta tamaño por imagen."""
    global _YUNET_DETECTOR

    if _YUNET_DETECTOR is None:
        _YUNET_DETECTOR = _create_yunet_detector(settings.yunet_model_path, input_size)
    else:
        _YUNET_DETECTOR.setInputSize(input_size)

    return _YUNET_DETECTOR


def _detect_faces_yunet(image_bgr: np.ndarray) -> list[FaceDetection]:
    """Detecta rostros con YuNet."""
    height, width = image_bgr.shape[:2]
    detector = _get_yunet_detector((width, height))

    _, faces = detector.detect(image_bgr)
    if faces is None:
        return []

    detections: list[FaceDetection] = []
    for row in faces:
        x, y, w, h = [int(round(value)) for value in row[:4]]
        x = max(0, x)
        y = max(0, y)
        w = max(1, min(w, width - x))
        h = max(1, min(h, height - y))
        score = float(row[-1])
        detections.append(
            FaceDetection(
                box=FaceBox(x=x, y=y, w=w, h=h),
                score=score,
                raw=row.astype(np.float32),
                detector_mode="yunet",
            )
        )

    return detections


def _load_haar_cascade() -> cv2.CascadeClassifier:
    """Carga el clasificador Haar frontal incluido en OpenCV."""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("No se pudo cargar el clasificador Haar de OpenCV.")
    return detector


_HAAR_DETECTOR = None


def _get_haar_detector() -> cv2.CascadeClassifier:
    """Inicializa detector Haar solo si se solicita fallback."""
    global _HAAR_DETECTOR

    if _HAAR_DETECTOR is None:
        _HAAR_DETECTOR = _load_haar_cascade()
    return _HAAR_DETECTOR


def _detect_faces_haar(image_bgr: np.ndarray) -> list[FaceDetection]:
    """Fallback Haar para desarrollo local sin modelos ONNX."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = _get_haar_detector().detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=6,
        minSize=(48, 48),
    )

    return [
        FaceDetection(
            box=FaceBox(x=int(x), y=int(y), w=int(w), h=int(h)),
            score=1.0,
            raw=None,
            detector_mode="haar",
        )
        for x, y, w, h in faces
    ]


def detect_faces(image_bgr: np.ndarray) -> list[FaceDetection]:
    """Detecta rostros según modo configurado."""
    if settings.face_detector_mode == "haar":
        return _detect_faces_haar(image_bgr)

    try:
        return _detect_faces_yunet(image_bgr)
    except RuntimeError:
        if settings.app_env == "development":
            logger.exception("YuNet no disponible. Usando fallback Haar en desarrollo.")
            return _detect_faces_haar(image_bgr)
        raise


def detect_single_face(
    image_bgr: np.ndarray,
    field_name: str,
    allow_largest_on_multiple: bool = False,
) -> FaceDetection:
    """Detecta un rostro válido en una imagen.

    Para document_image_b64 se puede seleccionar el rostro principal por área.
    Para live_image_b64 se exige exactamente un rostro.
    """
    faces = detect_faces(image_bgr)
    count = len(faces)

    if count == 0:
        logger.info("No se detectó rostro en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No se detectó un rostro en {field_name}.",
        )

    if count > 1:
        if allow_largest_on_multiple:
            selected_face = _select_largest_face(faces)
            logger.info(
                "Se detectaron %s candidatos en %s. Se seleccionó el rostro principal por área.",
                count,
                field_name,
            )
            return selected_face

        logger.info("Se detectaron múltiples rostros en campo %s.", field_name)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Se detectaron múltiples rostros en {field_name}.",
        )

    return faces[0]


def crop_face(image_bgr: np.ndarray, face_box: FaceBox, margin_ratio: float = 0.20) -> np.ndarray:
    """Recorta el rostro con margen para validaciones de calidad."""
    height, width = image_bgr.shape[:2]

    margin_x = int(face_box.w * margin_ratio)
    margin_y = int(face_box.h * margin_ratio)

    x1 = max(0, face_box.x - margin_x)
    y1 = max(0, face_box.y - margin_y)
    x2 = min(width, face_box.x + face_box.w + margin_x)
    y2 = min(height, face_box.y + face_box.h + margin_y)

    return image_bgr[y1:y2, x1:x2].copy()


def face_area_ratio(image_bgr: np.ndarray, face_box: FaceBox) -> float:
    """Calcula proporción de área del rostro respecto a la imagen completa."""
    height, width = image_bgr.shape[:2]
    total_area = max(1, height * width)
    return float(face_box.w * face_box.h) / float(total_area)

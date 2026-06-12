"""Configuración central del prototipo BioVerify-Zero."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Agrupa la configuración cargada desde variables de entorno."""

    app_name: str
    app_env: str
    app_mode: str
    log_level: str

    max_image_bytes: int
    max_total_body_bytes: int
    max_image_side: int
    normalized_face_size: int

    similarity_threshold: float
    allowed_origins: list[str]
    disable_biometric_logging: bool

    face_detector_mode: str
    face_embedding_mode: str
    yunet_model_path: Path
    sface_model_path: Path
    yunet_score_threshold: float
    yunet_nms_threshold: float
    yunet_top_k: int
    min_face_area_ratio: float
    min_blur_score: float
    min_brightness: float
    max_brightness: float


def _get_bool(name: str, default: bool) -> bool:
    """Convierte una variable de entorno a booleano."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    """Convierte una variable de entorno a entero con valor por defecto."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"La variable {name} debe ser entera.") from exc


def _get_float(name: str, default: float) -> float:
    """Convierte una variable de entorno a flotante con valor por defecto."""
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"La variable {name} debe ser numérica.") from exc


def _get_allowed_origins() -> list[str]:
    """Obtiene los orígenes permitidos para CORS."""
    raw_value = os.getenv("ALLOWED_ORIGINS", "http://localhost:7860")
    origins = [origin.strip() for origin in raw_value.split(",") if origin.strip()]
    return origins


def _project_root() -> Path:
    """Devuelve la raíz del proyecto."""
    return Path(__file__).resolve().parents[1]


def _get_path(name: str, default: str) -> Path:
    """Convierte una variable de entorno a ruta absoluta."""
    raw_value = os.getenv(name, default)
    path = Path(raw_value)
    if not path.is_absolute():
        path = _project_root() / path
    return path


def load_settings() -> Settings:
    """Carga la configuración de ejecución del servicio."""
    return Settings(
        app_name=os.getenv("APP_NAME", "BioVerify-Zero"),
        app_env=os.getenv("APP_ENV", "development"),
        app_mode=os.getenv("APP_MODE", "face_embedding_demo"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),

        max_image_bytes=_get_int("MAX_IMAGE_BYTES", 3_145_728),
        max_total_body_bytes=_get_int("MAX_TOTAL_BODY_BYTES", 8_000_000),
        max_image_side=_get_int("MAX_IMAGE_SIDE", 1280),
        normalized_face_size=_get_int("NORMALIZED_FACE_SIZE", 112),

        similarity_threshold=_get_float("SIMILARITY_THRESHOLD", 0.5),
        allowed_origins=_get_allowed_origins(),
        disable_biometric_logging=_get_bool("DISABLE_BIOMETRIC_LOGGING", True),

        face_detector_mode=os.getenv("FACE_DETECTOR_MODE", "yunet").strip().lower(),
        face_embedding_mode=os.getenv("FACE_EMBEDDING_MODE", "sface").strip().lower(),
        yunet_model_path=_get_path(
            "YUNET_MODEL_PATH",
            "models/face_detection_yunet_2023mar.onnx",
        ),
        sface_model_path=_get_path(
            "SFACE_MODEL_PATH",
            "models/face_recognition_sface_2021dec.onnx",
        ),
        yunet_score_threshold=_get_float("YUNET_SCORE_THRESHOLD", 0.85),
        yunet_nms_threshold=_get_float("YUNET_NMS_THRESHOLD", 0.30),
        yunet_top_k=_get_int("YUNET_TOP_K", 5000),
        min_face_area_ratio=_get_float("MIN_FACE_AREA_RATIO", 0.015),
        min_blur_score=_get_float("MIN_BLUR_SCORE", 18.0),
        min_brightness=_get_float("MIN_BRIGHTNESS", 35.0),
        max_brightness=_get_float("MAX_BRIGHTNESS", 225.0),
    )


settings = load_settings()

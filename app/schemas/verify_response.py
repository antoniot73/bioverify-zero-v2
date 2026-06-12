"""Esquemas de entrada y salida para verificación facial 1:1."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    """Solicitud de comparación facial.

    Las imágenes se reciben como Base64 o data URL para evitar el flujo multipart
    con archivos temporales gestionados por UploadFile.
    """

    consent_accepted: bool = Field(..., description="Consentimiento explícito no premarcado.")
    document_image_b64: str = Field(..., min_length=100, description="Imagen del documento en Base64 o data URL.")
    live_image_b64: str = Field(..., min_length=100, description="Imagen capturada en vivo en Base64 o data URL.")


class QualityReport(BaseModel):
    """Resultado de controles de calidad."""

    document_face_detected: bool
    live_face_detected: bool
    single_face_per_image: bool
    minimum_quality_passed: bool
    document_face_selected: str | None = None
    live_face_count: int | None = None
    document_face_area_ratio: float | None = None
    live_face_area_ratio: float | None = None
    document_brightness_ok: bool | None = None
    live_brightness_ok: bool | None = None
    document_sharpness_ok: bool | None = None
    live_sharpness_ok: bool | None = None


class VerifyResponse(BaseModel):
    """Respuesta segura de verificación 1:1."""

    verified: bool
    similarity_score: float
    threshold: float
    decision: str
    quality: QualityReport
    retention: str
    model_mode: str
    warning: str | None = None

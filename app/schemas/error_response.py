"""Esquemas de error controlado."""

from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Representa un error sin revelar información sensible."""

    detail: str
    code: str

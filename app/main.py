"""Aplicación principal BioVerify-Zero."""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.health_routes import router as health_router
from app.api.legal_routes import router as legal_router
from app.api.verify_routes import router as verify_router
from app.config import settings
from app.logging_config import configure_logging
from app.security.cors_policy import install_cors

configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI."""
    app = FastAPI(
        title=settings.app_name,
        version="0.2.0",
        description="Prototipo restringido de verificación facial 1:1 con embeddings temporales sin almacenamiento.",
    )

    install_cors(app)

    frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    app.include_router(health_router)
    app.include_router(legal_router)
    app.include_router(verify_router)

    @app.get("/")
    def index() -> FileResponse:
        """Sirve la interfaz web mínima."""
        return FileResponse(frontend_dir / "index.html")

    logger.info("%s iniciado en modo %s.", settings.app_name, settings.app_mode)
    return app


app = create_app()

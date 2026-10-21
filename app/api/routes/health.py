import urllib.request

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.db.database import engine
import logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready")
def readiness_check():
    database_available = False
    ollama_available = False

    # Check database
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        database_available = True

    except Exception as exc:
        logger.warning(
        "Readiness database check failed | error=%s",
        exc,
        )

    # Check Ollama
    try:
        with urllib.request.urlopen(
            f"{settings.OLLAMA_BASE_URL}/api/tags",
            timeout=1,
        ) as response:
            ollama_available = response.status == 200

    except Exception as exc:
        logger.warning(
        "Readiness Ollama check failed | error=%s",
        exc,
        )
    logger.info(
        "Readiness check completed | database=%s | ollama=%s",
        "available" if database_available else "unavailable",
        "available" if ollama_available else "unavailable",
    )
    # Service is ready only when all dependencies are available
    if not database_available or not ollama_available:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.ENVIRONMENT,
                "database": (
                    "available"
                    if database_available
                    else "unavailable"
                ),
                "ollama": (
                    "available"
                    if ollama_available
                    else "unavailable"
                ),
            },
        )

    return {
        "status": "ready",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "available",
        "ollama": "available",
    }
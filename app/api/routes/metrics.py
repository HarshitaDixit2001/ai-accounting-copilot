from fastapi import APIRouter

from app.core.config import settings
from app.core.metrics import (
    get_business_metrics,
    get_feedback_metrics,
    get_quality_metrics,
    get_rag_metrics,
    get_request_metrics,
)
from app.core.metrics import get_business_metrics

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get("")
def metrics():
    if not settings.EXPOSE_METRICS:
        return {
            "status": "disabled",
            "message": "Metrics endpoint is disabled.",
        }

    return {
        "requests": get_request_metrics(),
        "rag": get_rag_metrics(),
        "feedback": get_feedback_metrics(),
    }


@router.get("/feedback")
def feedback_metrics():
    return {
        "status": "ok",
        "feedback": get_feedback_metrics(),
    }



@router.get("/quality")
def quality_metrics():
    return {
        "status": "ok",
        "quality": get_quality_metrics(),
        "business": get_business_metrics(),
    }

@router.get("/summary")
def metrics_summary():
    if not settings.EXPOSE_METRICS:
        return {
            "status": "disabled",
            "message": "Metrics endpoint is disabled.",
        }

    return {
        "status": "ok",
        "requests": get_request_metrics(),
        "rag": get_rag_metrics(),
        "quality": get_quality_metrics(),
        "feedback": get_feedback_metrics(),
        "business": get_business_metrics(),
    }
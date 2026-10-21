from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.ai_audit import AIAuditLog


router = APIRouter(
    prefix="/audit",
    tags=["audit"],
)


def verify_audit_access(
    x_audit_api_key: str | None = Header(default=None),
):
    if not settings.AUDIT_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Audit access is not configured.",
        )

    if x_audit_api_key != settings.AUDIT_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid audit API key.",
        )


@router.get("/logs")
def get_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    _: None = Depends(verify_audit_access),
):
    limit = max(1, min(limit, 100))

    audit_logs = (
        db.query(AIAuditLog)
        .order_by(AIAuditLog.id.desc())
        .limit(limit)
        .all()
    )

    return {
        "status": "ok",
        "count": len(audit_logs),
        "logs": [
            {
                "id": log.id,
                "request_id": log.request_id,
                "question": log.question,
                "response": log.response,
                "sources": log.sources,
                "evaluator_score": log.evaluator_score,
                "created_at": log.created_at.isoformat(),
            }
            for log in audit_logs
        ],
    }
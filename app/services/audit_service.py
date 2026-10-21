import json

from sqlalchemy.orm import Session

from app.models.ai_audit import AIAuditLog
from app.services.data_governance import redact_sensitive_data

def record_ai_audit(
    db: Session,
    request_id: str,
    question: str,
    response: str,
    sources: list[dict],
    evaluator_score: float | None = None,
) -> AIAuditLog:
    audit_log = AIAuditLog(
    request_id=request_id,
    question=redact_sensitive_data(question),
    response=redact_sensitive_data(response),
    sources=json.dumps(sources),
    evaluator_score=(
        str(evaluator_score)
        if evaluator_score is not None
        else None
    ),
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log

from datetime import datetime, timedelta

from app.core.config import settings


def cleanup_expired_audits(db: Session) -> int:
    cutoff_date = datetime.utcnow() - timedelta(
        days=settings.AUDIT_RETENTION_DAYS
    )

    deleted_count = (
        db.query(AIAuditLog)
        .filter(AIAuditLog.created_at < cutoff_date)
        .delete(
            synchronize_session=False,
        )
    )

    db.commit()

    return deleted_count
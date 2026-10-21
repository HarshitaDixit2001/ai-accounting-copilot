from datetime import datetime, timedelta

from app.core.config import settings
from app.models.ai_audit import AIAuditLog
from app.services.audit_service import cleanup_expired_audits
from tests.conftest import TestingSessionLocal


def test_cleanup_expired_audits():
    db = TestingSessionLocal()

    try:
        expired_audit = AIAuditLog(
            request_id="expired-audit-test",
            question="Old question",
            response="Old response",
            sources="[]",
            evaluator_score="1.0",
            created_at=(
                datetime.utcnow()
                - timedelta(
                    days=settings.AUDIT_RETENTION_DAYS + 1
                )
            ),
        )

        current_audit = AIAuditLog(
            request_id="current-audit-test",
            question="Current question",
            response="Current response",
            sources="[]",
            evaluator_score="1.0",
        )

        db.add_all(
            [
                expired_audit,
                current_audit,
            ]
        )
        db.commit()

        deleted_count = cleanup_expired_audits(db)

        assert deleted_count >= 1

        expired_record = (
            db.query(AIAuditLog)
            .filter(
                AIAuditLog.request_id
                == "expired-audit-test"
            )
            .first()
        )

        current_record = (
            db.query(AIAuditLog)
            .filter(
                AIAuditLog.request_id
                == "current-audit-test"
            )
            .first()
        )

        assert expired_record is None
        assert current_record is not None

    finally:
        db.close()
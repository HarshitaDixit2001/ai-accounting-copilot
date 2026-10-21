from app.models.ai_audit import AIAuditLog
from app.services.audit_service import record_ai_audit
from tests.conftest import TestingSessionLocal


def test_record_ai_audit(setup_test_database):
    db = TestingSessionLocal()

    try:
        audit_log = record_ai_audit(
            db=db,
            request_id="audit-test-001",
            question="How do I record rent paid in cash?",
            response="Debit Rent Expense and Credit Cash.",
            sources=[
                {
                    "source": "journal_entries.txt",
                    "chunk_id": 1,
                    "similarity": 0.82,
                }
            ],
            evaluator_score=1.0,
        )

        assert isinstance(audit_log, AIAuditLog)
        assert audit_log.id is not None
        assert audit_log.request_id == "audit-test-001"
        assert audit_log.question == "How do I record rent paid in cash?"
        assert audit_log.response == "Debit Rent Expense and Credit Cash."
        assert audit_log.evaluator_score == "1.0"
        assert "journal_entries.txt" in audit_log.sources

    finally:
        db.close()
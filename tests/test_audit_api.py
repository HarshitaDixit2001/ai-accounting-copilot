from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.models.ai_audit import AIAuditLog
from tests.conftest import TestingSessionLocal


client = TestClient(app)


def create_test_audit_log():
    db = TestingSessionLocal()

    try:
        audit_log = AIAuditLog(
            request_id="audit-security-test-001",
            question="How do I record rent paid in cash?",
            response="Debit Rent Expense and Credit Cash.",
            sources='[{"source": "journal_entries.txt"}]',
            evaluator_score="1.0",
        )

        db.add(audit_log)
        db.commit()
    finally:
        db.close()


def test_audit_logs_requires_api_key():
    create_test_audit_log()

    response = client.get("/audit/logs")

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid audit API key."


def test_audit_logs_rejects_invalid_api_key():
    create_test_audit_log()

    response = client.get(
        "/audit/logs",
        headers={
            "X-Audit-Api-Key": "wrong-key",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid audit API key."


def test_audit_logs_accepts_valid_api_key():
    create_test_audit_log()

    response = client.get(
        "/audit/logs",
        headers={
            "X-Audit-Api-Key": settings.AUDIT_API_KEY,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["count"] >= 1
    assert "logs" in body
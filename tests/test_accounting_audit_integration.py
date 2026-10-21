from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.ai_audit import AIAuditLog
from tests.conftest import TestingSessionLocal


client = TestClient(app)


def test_accounting_intelligence_creates_audit_log():
    with patch(
        "app.api.routes.accounting.explain_accounting_concept",
        new=AsyncMock(
            return_value={
                "response": "Debit Rent Expense and Credit Cash.",
                "journal_entry": None,
                "sources": [
                    {
                        "source": "journal_entries.txt",
                        "chunk_id": 1,
                        "similarity": 0.82,
                        "content": (
                            "Payment of Rent: Debit: Rent Expense; "
                            "Credit: Cash or Bank."
                        ),
                    }
                ],
                "confidence": 0.82,
            }
        ),
    ):
        response = client.post(
            "/accounting/intelligence",
            json={
                "prompt": "How do I record rent paid in cash?"
            },
        )

    assert response.status_code == 200

    body = response.json()

    assert body["response"] == (
        "Debit Rent Expense and Credit Cash."
    )
    assert body["sources"]

    db = TestingSessionLocal()

    try:
        audit_log = (
            db.query(AIAuditLog)
            .filter(
                AIAuditLog.question
                == "How do I record rent paid in cash?"
            )
            .order_by(AIAuditLog.id.desc())
            .first()
        )

        assert audit_log is not None
        assert audit_log.request_id
        assert audit_log.response == (
            "Debit Rent Expense and Credit Cash."
        )
        assert "journal_entries.txt" in audit_log.sources
        assert audit_log.evaluator_score is not None

    finally:
        db.close()

def test_accounting_intelligence_records_business_metric():
    from app.core.metrics import get_business_metrics

    before = get_business_metrics()

    with patch(
        "app.api.routes.accounting.explain_accounting_concept",
        new=AsyncMock(
            return_value={
                "response": "Debit Rent Expense and Credit Cash.",
                "journal_entry": None,
                "sources": [
                    {
                        "source": "journal_entries.txt",
                        "chunk_id": 1,
                        "similarity": 0.82,
                        "content": (
                            "Payment of Rent: Debit: Rent Expense; "
                            "Credit: Cash or Bank."
                        ),
                    }
                ],
                "confidence": 0.82,
            }
        ),
    ):
        response = client.post(
            "/accounting/intelligence",
            json={
                "prompt": "How do I record rent paid in cash?"
            },
        )

    assert response.status_code == 200

    after = get_business_metrics()

    assert (
        after["accounting_questions_answered"]
        == before["accounting_questions_answered"] + 1
    )


def test_transaction_explanation_records_business_metric():
    from app.core.metrics import get_business_metrics

    before = get_business_metrics()

    with patch(
        "app.api.routes.accounting.explain_transaction",
        new=AsyncMock(
            return_value={
                "response": "Debit Rent Expense and Credit Cash.",
                "journal_entry": None,
                "sources": [
                    {
                        "source": "journal_entries.txt",
                        "chunk_id": 1,
                        "similarity": 0.82,
                        "content": (
                            "Payment of Rent: Debit: Rent Expense; "
                            "Credit: Cash or Bank."
                        ),
                    }
                ],
                "confidence": 0.82,
            }
        ),
    ):
        response = client.post(
            "/accounting/transaction/explain",
            json={
                "description": "Rent paid in cash ₹25000"
            },
        )

    assert response.status_code == 200

    after = get_business_metrics()

    assert (
        after["transaction_explanations"]
        == before["transaction_explanations"] + 1
    )
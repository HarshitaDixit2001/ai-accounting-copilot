import pytest
from unittest.mock import AsyncMock, patch
from app.services.accounting_intelligence import calculate_retrieval_confidence

from app.services.accounting_intelligence import (
    explain_accounting_concept,
    explain_transaction,
)

from app.services.accounting_intelligence import (
    calculate_retrieval_confidence,
    classify_transaction,
    extract_amount,
)

@pytest.mark.asyncio
async def test_explain_accounting_concept():
    with patch(
        "app.services.accounting_intelligence.ask_rag_assistant",
        new_callable=AsyncMock,
        return_value={
            "response": "Debit Rent Expense and Credit Cash.",
            "sources": [],
        },
    ):
        result = await explain_accounting_concept(
            "How do I record rent paid in cash?"
        )

    assert result["response"] == "Debit Rent Expense and Credit Cash."
    assert result["sources"] == []

@pytest.mark.asyncio
async def test_explain_accounting_concept_returns_sources():
    fake_result = {
        "response": "A journal entry records a financial transaction.",
        "sources": [
            {
                "source": "journal_entries.txt",
                "chunk_id": 0,
                "similarity": 0.82,
            }
        ],
    }

    with patch(
        "app.services.accounting_intelligence.ask_rag_assistant",
        new_callable=AsyncMock,
        return_value=fake_result,
    ):
        result = await explain_accounting_concept(
            "What is a journal entry?"
        )

    assert result["response"]
    assert result["sources"]

    source = result["sources"][0]

    assert source["source"] == "journal_entries.txt"
    assert source["chunk_id"] == 0
    assert source["similarity"] == 0.82

@pytest.mark.asyncio
async def test_explain_accounting_concept_when_no_relevant_context():
    fake_result = {
        "response": (
            "The provided accounting knowledge does not contain "
            "enough information to answer this question."
        ),
        "sources": [],
    }

    with patch(
        "app.services.accounting_intelligence.ask_rag_assistant",
        new_callable=AsyncMock,
        return_value=fake_result,
    ):
        result = await explain_accounting_concept(
            "What is the capital of France?"
        )

    assert result["response"]
    assert "not contain enough information" in result["response"]
    assert result["sources"] == []

@pytest.mark.asyncio
async def test_explain_transaction():
    fake_result = {
        "response": "Debit Rent Expense and Credit Cash.",
        "sources": [
            {
                "source": "financial_transactions.txt",
                "chunk_id": 1,
                "similarity": 0.81,
            }
        ],
    }

    with patch(
        "app.services.accounting_intelligence.ask_rag_assistant",
        new_callable=AsyncMock,
        return_value=fake_result,
    ):
        result = await explain_transaction(
            "Rent paid in cash"
        )

    assert result["response"] == "Debit Rent Expense and Credit Cash."
    assert result["sources"]
    assert result["sources"][0]["source"] == "financial_transactions.txt"
    assert result["sources"][0]["chunk_id"] == 1
    assert result["sources"][0]["similarity"] == 0.81

@pytest.mark.asyncio
async def test_explain_transaction_when_no_relevant_context():
    fake_result = {
        "response": (
            "The provided accounting knowledge does not contain "
            "enough information to answer this question."
        ),
        "sources": [],
    }

    with patch(
        "app.services.accounting_intelligence.ask_rag_assistant",
        new_callable=AsyncMock,
        return_value=fake_result,
    ):
        result = await explain_transaction(
            "How do I repair a car engine?"
        )

    assert result["response"]
    assert "not contain enough information" in result["response"]
    assert result["sources"] == []

@pytest.mark.asyncio
async def test_explain_transaction_preserves_multiple_sources():
    fake_result = {
        "response": "Debit Rent Expense and Credit Cash.",
        "sources": [
            {
                "source": "financial_transactions.txt",
                "chunk_id": 1,
                "similarity": 0.81,
            },
            {
                "source": "journal_entries.txt",
                "chunk_id": 2,
                "similarity": 0.76,
            },
        ],
    }

    with patch(
        "app.services.accounting_intelligence.ask_rag_assistant",
        new_callable=AsyncMock,
        return_value=fake_result,
    ):
        result = await explain_transaction("Rent paid in cash")

    assert result["response"] == "Debit Rent Expense and Credit Cash."
    assert len(result["sources"]) == 2

    for source in result["sources"]:
        assert source["source"]
        assert isinstance(source["chunk_id"], int)
        assert isinstance(source["similarity"], float)
        assert 0.0 <= source["similarity"] <= 1.0

def test_accounting_intelligence_endpoint_uses_request_body():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)

    response = client.post(
        "/accounting/intelligence",
        json={"prompt": "What is a journal entry?"},
    )

    assert response.status_code == 200
    assert "response" in response.json()
    assert "sources" in response.json()


def test_transaction_explanation_endpoint_uses_request_body():
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)

    response = client.post(
        "/accounting/transaction/explain",
        json={"description": "Rent paid in cash"},
    )

    assert response.status_code == 200
    assert "response" in response.json()
    assert "sources" in response.json()

def test_calculate_retrieval_confidence_returns_strongest_similarity():
    sources = [
        {"source": "a.txt", "chunk_id": 0, "similarity": 0.61},
        {"source": "b.txt", "chunk_id": 1, "similarity": 0.83},
        {"source": "c.txt", "chunk_id": 2, "similarity": 0.72},
    ]

    assert calculate_retrieval_confidence(sources) == 0.83


def test_calculate_retrieval_confidence_returns_zero_without_sources():
    assert calculate_retrieval_confidence([]) == 0.0


def test_calculate_retrieval_confidence_is_bounded():
    sources = [
        {"source": "a.txt", "chunk_id": 0, "similarity": 1.4},
    ]

    assert calculate_retrieval_confidence(sources) == 1.0

def test_extract_amount_supports_rupee_format():
    assert extract_amount("Rent paid in cash ₹25,000") == 25000.0


def test_extract_amount_supports_plain_number():
    assert extract_amount("Rent paid in cash 25000") == 25000.0


def test_extract_amount_returns_zero_when_missing():
    assert extract_amount("Rent paid in cash") == 0.0


def test_classify_rent_paid_in_cash():
    journal_entry = classify_transaction(
        "Rent paid in cash ₹25000",
        25000.0,
    )

    assert journal_entry is not None
    assert journal_entry.debit.account == "Rent Expense"
    assert journal_entry.debit.amount == 25000.0
    assert journal_entry.credit.account == "Cash"
    assert journal_entry.credit.amount == 25000.0


def test_classify_unsupported_transaction_returns_none():
    journal_entry = classify_transaction(
        "Office supplies purchased",
        5000.0,
    )

    assert journal_entry is None
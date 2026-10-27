from unittest import result
from app.services.evaluator import evaluate_accounting_response


def test_evaluator_accepts_grounded_accounting_response():
    result = evaluate_accounting_response(
        question="How do I record rent paid in cash?",
        response=(
            "Debit Rent Expense and credit Cash because the rent "
            "payment increases the expense and decreases cash."
        ),
        sources=[
            {
                "source": "financial_transactions.txt",
                "chunk_id": 1,
                "content": (
                    "Payment of Rent: Debit: Rent Expense; "
                    "Credit: Cash or Bank."
                ),
            }
        ],
    )

    assert result["passed"] is True
    assert result["score"] >= 0.75
    assert result["checks"]["response_present"] is True
    assert result["checks"]["sources_present"] is True
    assert result["checks"]["accounting_terminology"] is True
    assert result["checks"]["grounded_in_sources"] is True


def test_evaluator_rejects_empty_response():
    result = evaluate_accounting_response(
        question="How do I record rent?",
        response="",
        sources=[],
    )

    assert result["passed"] is False
    assert result["checks"]["response_present"] is False


def test_evaluator_accepts_safe_abstention():
    result = evaluate_accounting_response(
        question="How do I account for an unsupported transaction?",
        response=(
            "The provided accounting knowledge does not contain "
            "enough information to answer this question."
        ),
        sources=[],
    )

    assert result["passed"] is True
    assert result["checks"]["safe_abstention"] is True


def test_evaluator_returns_structured_result():
    result = evaluate_accounting_response(
        question="What is a debit?",
        response="A debit is an accounting entry recorded on the debit side.",
        sources=[
            {
                "source": "journal_entries.txt",
                "chunk_id": 0,
                "content": "A debit is recorded on the debit side.",
            }
        ],
    )

    assert "score" in result
    assert "passed" in result
    assert "checks" in result
    assert "passed_checks" in result
    assert "total_checks" in result


def test_evaluator_rejects_irrelevant_accounting_response():
    result = evaluate_accounting_response(
        question="How do I calculate depreciation?",
        response=(
            "Debit Rent Expense and credit Cash for rent paid."
        ),
        sources=[
            {
                "source": "financial_transactions.txt",
                "chunk_id": 1,
                "content": (
                    "Payment of Rent: Debit Rent Expense; "
                    "Credit Cash."
                ),
            }
        ],
    )

    assert result["checks"]["question_relevance"] is False
    assert result["passed"] is False

def test_evaluator_rejects_sources_without_relevant_evidence():
    result = evaluate_accounting_response(
        question="How do I calculate depreciation?",
        response=(
            "Depreciation is an expense that allocates an asset's "
            "cost over its useful life."
        ),
        sources=[
            {
                "source": "financial_transactions.txt",
                "chunk_id": 1,
                "content": (
                    "Payment of Rent: Debit Rent Expense; "
                    "Credit Cash."
                ),
            }
        ],
    )

    assert result["checks"]["grounded_in_sources"] is False
    assert result["passed"] is False



def test_evaluator_reports_failed_checks():
    result = evaluate_accounting_response(
        question="How do I calculate depreciation?",
        response=(
            "Depreciation is calculated by dividing the depreciable "
            "amount by the useful life of the asset."
        ),
        sources=[
            {
                "source": "financial_transactions.txt",
                "chunk_id": 1,
                "content": (
                    "Payment of Rent: Debit Rent Expense; "
                    "Credit Cash."
                ),
            }
        ],
    )

    assert "grounded_in_sources" in result["failed_checks"]
    assert result["passed"] is False

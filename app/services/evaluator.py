from typing import Any

from app.core.metrics import record_evaluator_score


ABSTENTION_INDICATORS = [
    "not enough information",
    "does not contain enough information",
    "cannot answer",
    "unable to answer",
    "do not have enough information",
    "not available",
]


def evaluate_accounting_response(
    question: str,
    response: str,
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Evaluate an accounting assistant response using a deterministic rubric.

    Normal responses are evaluated for:
    - response completeness
    - source availability
    - grounding evidence
    - accounting terminology
    - question relevance

    Unsupported questions are evaluated separately for:
    - safe abstention
    """

    question_lower = question.lower().strip()
    response_lower = response.lower().strip()

    is_abstention = any(
        indicator in response_lower
        for indicator in ABSTENTION_INDICATORS
    )

    # ---------------------------------------------------------
    # Safe-abstention evaluation
    # ---------------------------------------------------------
    if is_abstention:
        checks = {
            "response_present": len(response_lower) >= 20,
            "safe_abstention": True,
            "no_unsupported_claim": len(sources) == 0,
        }

        passed_checks = sum(checks.values())
        total_checks = len(checks)

        score = round(
            passed_checks / total_checks,
            3,
        )

        record_evaluator_score(score)

        return {
            "score": score,
            "passed": score >= 0.75,
            "evaluation_type": "abstention",
            "checks": checks,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
        }

    # ---------------------------------------------------------
    # Normal-response evaluation
    # ---------------------------------------------------------

    checks: dict[str, bool] = {}

    # Response should contain meaningful content.
    checks["response_present"] = len(response_lower) >= 20

    # Normal answers should have retrieved evidence.
    checks["sources_present"] = len(sources) > 0

    # Response should contain accounting terminology.
    accounting_terms = [
        "debit",
        "credit",
        "expense",
        "asset",
        "liability",
        "revenue",
        "cash",
        "bank",
        "journal entry",
    ]

    checks["accounting_terminology"] = any(
        term in response_lower
        for term in accounting_terms
    )

    # Retrieved evidence should contain actual source content.
    checks["grounded_in_sources"] = (
        any(
            source.get("source")
            and source.get("content")
            for source in sources
        )
        if sources
        else False
    )

    # Question should influence the response.
    question_terms = [
        word
        for word in question_lower.split()
        if len(word) > 3
    ]

    checks["question_relevance"] = (
        any(
            term in response_lower
            for term in question_terms
        )
        if question_terms
        else True
    )

    passed_checks = sum(checks.values())
    total_checks = len(checks)

    score = (
        round(
            passed_checks / total_checks,
            3,
        )
        if total_checks
        else 0.0
    )

    record_evaluator_score(score)

    return {
        "score": score,
        "passed": (
            score >= 0.75
            and checks["question_relevance"]
            and checks["grounded_in_sources"]
        ),
        "evaluation_type": "normal_response",
        "checks": checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
    }
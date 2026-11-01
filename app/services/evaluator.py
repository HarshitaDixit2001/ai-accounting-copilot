
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
    record_metrics: bool = True,
) -> dict[str, Any]:
    """
    Evaluate an accounting assistant response using a deterministic rubric.

    This is a heuristic evaluation, not proof of factual correctness.
    Normal responses require a passing score, question relevance,
    and source overlap. Abstentions are evaluated separately.
    """

    question_lower = question.lower().strip()
    response_lower = response.lower().strip()

    is_abstention = any(
        indicator in response_lower
        for indicator in ABSTENTION_INDICATORS
    )

    # Safe-abstention evaluation
    if is_abstention:
        checks = {
            "response_present": len(response_lower) >= 20,
            "safe_abstention": True,
            "no_unsupported_claim": len(sources) == 0,
        }

        passed_checks = sum(checks.values())
        total_checks = len(checks)
        score = round(passed_checks / total_checks, 3)

        if record_metrics:
            record_evaluator_score(score)

        return {
            "score": score,
            "passed": score >= 0.75,
            "evaluation_type": "abstention",
            "checks": checks,
            "failed_checks": [
                name for name, passed in checks.items() if not passed
            ],
            "passed_checks": passed_checks,
            "total_checks": total_checks,
        }

    # Normal-response evaluation
    checks: dict[str, bool] = {}

    checks["response_present"] = len(response_lower) >= 20
    checks["sources_present"] = len(sources) > 0

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
        term in response_lower for term in accounting_terms
    )

    # Heuristic source overlap; this does not prove semantic support.
    source_text = " ".join(
        str(source.get("content", ""))
        for source in sources
        if source.get("content")
    ).lower()

    def meaningful_terms(text: str) -> set[str]:
        return {
            word.strip(".,!?;:()[]{}\"'")
            for word in text.split()
            if len(word.strip(".,!?;:()[]{}\"'")) > 3
        }

    response_terms = meaningful_terms(response_lower)
    source_terms = meaningful_terms(source_text)

    checks["grounded_in_sources"] = (
        len(response_terms & source_terms) >= 2
    )

    question_terms = [
        word.strip(".,!?;:()[]{}\"'")
        for word in question_lower.split()
        if len(word.strip(".,!?;:()[]{}\"'")) > 3
    ]

    checks["question_relevance"] = (
        any(term in response_lower for term in question_terms)
        if question_terms
        else True
    )

    passed_checks = sum(checks.values())
    total_checks = len(checks)
    score = round(passed_checks / total_checks, 3) if total_checks else 0.0
    if record_metrics:
        record_evaluator_score(score)

    failed_checks = [
        name for name, passed in checks.items() if not passed
    ]

    return {
        "score": score,
        "passed": (
            score >= 0.75
            and checks["question_relevance"]
            and checks["grounded_in_sources"]
        ),
        "evaluation_type": "normal_response",
        "checks": checks,
        "failed_checks": failed_checks,
        "passed_checks": passed_checks,
        "total_checks": total_checks,
    }

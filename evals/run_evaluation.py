import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from app.services.accounting_intelligence import (
    explain_accounting_concept,
    explain_transaction,
)
from app.services.evaluator import evaluate_accounting_response

BASE_DIR = Path(__file__).resolve().parent
TEST_CASES_FILE = BASE_DIR / "test_cases.json"


def load_test_cases() -> list[dict]:
    """Load representative evaluation cases from JSON."""
    with TEST_CASES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)

def load_baseline() -> dict:
    """Load the stored evaluation baseline."""
    baseline_file = BASE_DIR / "results" / "baseline.json"

    with baseline_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)
def keyword_match_score(
    response: str,
    expected_keywords: list[str],
) -> float:
    """Measure how many expected keywords appear in the answer."""
    if not expected_keywords:
        return 1.0

    response_lower = response.lower()

    matches = sum(
        1
        for keyword in expected_keywords
        if keyword.lower() in response_lower
    )

    return round(matches / len(expected_keywords), 3)


def source_match_score(
    sources: list[dict],
    expected_sources: list[str],
) -> float:
    """Measure whether expected knowledge-base sources were retrieved."""
    if not expected_sources:
        return 1.0

    retrieved_sources = {
        source["source"]
        for source in sources
    }

    matches = sum(
        1
        for expected_source in expected_sources
        if expected_source in retrieved_sources
    )

    return round(matches / len(expected_sources), 3)


def grounding_score(
    response: str,
    sources: list[dict],
) -> float:
    """
    Lightweight heuristic grounding grader.

    Measures whether meaningful terms from the retrieved
    evidence also appear in the generated response.
    """
    if not sources:
        return 0.0

    response_lower = response.lower()

    evidence_text = " ".join(
        source.get("content", "")
        for source in sources
    ).lower()

    evidence_terms = {
        word.strip(".,:;()[]\"'")
        for word in evidence_text.split()
        if len(word.strip(".,:;()[]\"'")) >= 5
    }

    if not evidence_terms:
        return 0.0

    matches = sum(
        1
        for term in evidence_terms
        if term in response_lower
    )

    return round(
        min(matches / 10, 1.0),
        3,
    )


def response_completeness_score(response: str) -> float:
    """Measure whether the generated response contains useful content."""
    if not response or not response.strip():
        return 0.0

    word_count = len(response.split())

    if word_count >= 20:
        return 1.0

    if word_count >= 10:
        return 0.5

    return 0.0


async def evaluate_case(test_case: dict) -> dict:
    """Run one evaluation case and calculate evaluation metrics."""
    category = test_case["category"]
    question = test_case["question"]

    if category == "transaction":
        result = await explain_transaction(question)
    else:
        result = await explain_accounting_concept(question)

    response = result["response"]
    sources = result["sources"]

    keyword_score = keyword_match_score(
        response,
        test_case["expected_keywords"],
    )

    source_score = source_match_score(
        sources,
        test_case["expected_sources"],
    )

    grounding = grounding_score(
        response,
        sources,
    )

    completeness = response_completeness_score(
        response
    )
    evaluator_result = evaluate_accounting_response(
        question=question,
        response=response,
        sources=sources,
    )
    if category == "unsupported":
        passed = (
            keyword_score >= 0.5
            and source_score >= 1.0
            and len(sources) == 0
            and completeness >= 0.5
        )
    else:
        passed = (
            keyword_score >= 0.5
            and source_score >= 1.0
            and grounding >= 0.2
            and completeness >= 0.5
        )

    return {
        "id": test_case["id"],
        "category": category,
        "question": question,
        "keyword_score": keyword_score,
        "source_score": source_score,
        "grounding_score": grounding,
        "completeness_score": completeness,
        "evaluator_score": evaluator_result["score"],
        "evaluator_passed": evaluator_result["passed"],
        "evaluator_type": evaluator_result["evaluation_type"],
        "evaluator_checks": evaluator_result["checks"],
        "confidence": result["confidence"],
        "retrieved_sources": [
            {
                "source": source["source"],
                "chunk_id": source["chunk_id"],
                "similarity": round(
                    source["similarity"],
                    3,
                ),
            }
            for source in sources
        ],
        "passed": passed,
    }


async def main() -> None:
    """Run the evaluation dataset."""

    test_cases = load_test_cases()

    parser = argparse.ArgumentParser(
        description="Run AI Accounting Copilot evaluation."
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run the first two evaluation cases.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Run only the first N evaluation cases.",
    )
    parser.add_argument(
        "--id",
        type=str,
        help="Run a specific evaluation case by ID.",
    )
    args = parser.parse_args()

    if args.id is not None:
        test_cases = [
            test_case
            for test_case in test_cases
            if test_case["id"] == args.id
        ]

        if not test_cases:
            raise ValueError(
                f"Evaluation case not found: {args.id}"
            )

        print(
            f"Running evaluation case: "
            f"{args.id}"
        )

    elif args.limit is not None:
        if args.limit <= 0:
                raise ValueError("--limit must be greater than zero.")

        test_cases = test_cases[:args.limit]

        print(
            f"Running evaluation with "
            f"{len(test_cases)} case(s)..."
        )

    elif args.fast:
        test_cases = test_cases[:2]
        print("Running FAST evaluation mode...")

    else:
        print("Running FULL evaluation mode...")

    results = []

    for test_case in test_cases:
        result = await evaluate_case(test_case)
        results.append(result)

        print(
            f"{result['id']}: "
            f"keyword={result['keyword_score']:.2f}, "
            f"source={result['source_score']:.2f}, "
            f"grounding={result['grounding_score']:.2f}, "
            f"completeness={result['completeness_score']:.2f}, "
            f"evaluator={result['evaluator_score']:.2f}, "
            f"confidence={result['confidence']:.3f}, "
            f"passed={result['passed']}"
        )

        print("  Retrieved sources:")

        for source in result["retrieved_sources"]:
            print(
                f"    - {source['source']} "
                f"(chunk={source['chunk_id']}, "
                f"similarity={source['similarity']:.3f})"
            )

    if not results:
        raise RuntimeError(
            "No evaluation cases were selected."
        )

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    average_keyword_score = round(
        sum(
            result["keyword_score"]
            for result in results
        )
        / len(results),
        3,
    )

    average_source_score = round(
        sum(
            result["source_score"]
            for result in results
        )
        / len(results),
        3,
    )

    average_grounding_score = round(
        sum(
            result["grounding_score"]
            for result in results
        )
        / len(results),
        3,
    )

    average_completeness_score = round(
        sum(
            result["completeness_score"]
            for result in results
        )
        / len(results),
        3,
    )
    average_evaluator_score = round(
    sum(
        result["evaluator_score"]
        for result in results
    )
    / len(results),
    3,
    )

    average_confidence = round(
        sum(
            result["confidence"]
            for result in results
        )
        / len(results),
        3,
    )
    pass_rate = round(
        passed / len(results),
        3,
    )

    baseline_pass_rate = None
    regression_detected = False

    if (
        args.id is None
        and args.limit is None
        and not args.fast
    ):
        baseline = load_baseline()

        baseline_pass_rate = baseline["pass_rate"]

        baseline_keyword_score = baseline[
            "average_keyword_score"
        ]
        baseline_source_score = baseline[
            "average_source_score"
        ]
        baseline_grounding_score = baseline[
            "average_grounding_score"
        ]
        baseline_completeness_score = baseline[
            "average_completeness_score"
        ]

        regression_detected = (
            pass_rate < baseline_pass_rate
            or average_keyword_score < baseline_keyword_score
            or average_source_score < baseline_source_score
            or average_grounding_score < baseline_grounding_score
            or average_completeness_score < baseline_completeness_score
            or average_evaluator_score < minimum_evaluator_score
        )

        if regression_detected:
            print("REGRESSION DETECTED")
            print(
                f"  Pass rate: "
                f"{pass_rate:.3f} "
                f"(baseline {baseline_pass_rate:.3f})"
            )
            print(
                f"  Keyword score: "
                f"{average_keyword_score:.3f} "
                f"(baseline {baseline_keyword_score:.3f})"
            )
            print(
                f"  Source score: "
                f"{average_source_score:.3f} "
                f"(baseline {baseline_source_score:.3f})"
            )
            print(
                f"  Grounding: "
                f"{average_grounding_score:.3f} "
                f"(baseline {baseline_grounding_score:.3f})"
            )
            print(
                f"  Completeness: "
                f"{average_completeness_score:.3f} "
                f"(baseline {baseline_completeness_score:.3f})"
            )
        else:
            print("Regression check passed.")

    if regression_detected:
        print("REGRESSION DETECTED")
        print(
            f"  Pass rate:       {pass_rate:.3f} "
            f"(baseline {baseline_pass_rate:.3f})"
        )
        print(
            f"  Keyword score:   {average_keyword_score:.3f} "
            f"(baseline {baseline_keyword_score:.3f})"
        )
        print(
            f"  Source score:    {average_source_score:.3f} "
            f"(baseline {baseline_source_score:.3f})"
        )
        print(
            f"  Grounding:       {average_grounding_score:.3f} "
            f"(baseline {baseline_grounding_score:.3f})"
        )
        print(
            f"  Completeness:    {average_completeness_score:.3f} "
            f"(baseline {baseline_completeness_score:.3f})"
        )
        print(
        f"  Evaluator score: "
        f"{average_evaluator_score:.3f} "
        f"(minimum {minimum_evaluator_score:.3f})"
        )
    else:
        print("Regression check passed.")
    results_dir = BASE_DIR / "results"
    results_dir.mkdir(exist_ok=True)

    report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "total_cases": len(results),
    "passed_cases": passed,
    "pass_rate": pass_rate,
    "baseline_pass_rate": baseline_pass_rate,
    "regression_detected": regression_detected,
    "average_keyword_score": average_keyword_score,
    "average_source_score": average_source_score,
    "average_grounding_score": average_grounding_score,
    "average_completeness_score": average_completeness_score,
    "average_evaluator_score": average_evaluator_score,
    "average_confidence": average_confidence,
    "cases": results,
}
    if args.id is not None or args.limit is not None or args.fast:
        report_file = results_dir / "fast_evaluation_report.json"
    else:
        report_file = results_dir / "evaluation_report.json"

    with report_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )
    print()
    print(
        f"Evaluation report saved to: "
        f"{report_file}"
    )

    if (
        args.id is None
        and args.limit is None
        and not args.fast
    ):
        minimum_pass_rate = 0.80

        if pass_rate < minimum_pass_rate:
            raise RuntimeError(
                f"Evaluation failed: pass rate "
                f"{pass_rate:.1%} is below the required "
                f"threshold of {minimum_pass_rate:.1%}."
            )

        print(
            f"Evaluation quality gate passed "
            f"({pass_rate:.1%} >= "
            f"{minimum_pass_rate:.1%})"
        )


if __name__ == "__main__":
    asyncio.run(main())
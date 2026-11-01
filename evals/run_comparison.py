
import argparse
import asyncio
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.rag.retriever import retrieve_relevant_chunks
from app.services.accounting_intelligence import (
    explain_accounting_concept,
    explain_transaction,
)
from app.services.evaluator import evaluate_accounting_response

from evals.run_evaluation import (
    keyword_match_score,
    source_match_score,
    grounding_score,
    response_completeness_score,
)


BASE_DIR = Path(__file__).resolve().parent
TEST_CASES_FILE = BASE_DIR / "test_cases.json"
RESULTS_DIR = BASE_DIR / "results" / "comparisons"

DEFAULT_MODELS = [
    "qwen3:8b",
    "llama3.2:latest",
]

MINIMUM_PASS_RATE = 0.80
MINIMUM_EVALUATOR_SCORE = 0.75


def load_test_cases() -> list[dict]:
    with TEST_CASES_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_fingerprint(data: object) -> str:
    serialized = json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(serialized).hexdigest()


async def evaluate_case(
    test_case: dict,
    model: str,
    retrieved_chunks: list[dict],
) -> dict:
    question = test_case["question"]
    category = test_case["category"]

    common_arguments = {
        "model": model,
        "record_metrics": False,
        "include_metadata": True,
        "retrieved_chunks": retrieved_chunks,
    }

    if category == "transaction":
        result = await explain_transaction(
            question,
            **common_arguments,
        )
    else:
        result = await explain_accounting_concept(
            question,
            **common_arguments,
        )

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

    grounding = grounding_score(response, sources)
    completeness = response_completeness_score(response)

    evaluator_result = evaluate_accounting_response(
        question=question,
        response=response,
        sources=sources,
        record_metrics=False,
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

    metadata = result.get("generation_metadata")

    evidence_fingerprint = calculate_fingerprint(
        retrieved_chunks
    )

    return {
        "id": test_case["id"],
        "category": category,
        "question": question,
        "response": response,
        "keyword_score": keyword_score,
        "source_score": source_score,
        "grounding_score": grounding,
        "completeness_score": completeness,
        "evaluator_score": evaluator_result["score"],
        "evaluator_passed": evaluator_result["passed"],
        "passed": passed,
        "confidence": result["confidence"],
        "retrieved_sources": [
            {
                "source": source["source"],
                "chunk_id": source["chunk_id"],
                "similarity": round(source["similarity"], 3),
            }
            for source in sources
        ],
        "generation_metadata": metadata,
        "evidence_fingerprint": evidence_fingerprint,
    }


async def evaluate_model(
    model: str,
    test_cases: list[dict],
    evidence_by_case: dict[str, list[dict]],
) -> dict:
    print(f"\nEvaluating model: {model}", flush=True)

    results = []

    for index, test_case in enumerate(test_cases, start=1):
        case_start = time.perf_counter()

        print(
            f"[{index}/{len(test_cases)}] "
            f"Starting {test_case['id']}...",
            flush=True,
        )

        result = await evaluate_case(
            test_case,
            model,
            evidence_by_case[test_case["id"]],
        )

        elapsed_seconds = time.perf_counter() - case_start

        results.append(result)

        metadata = result["generation_metadata"] or {}

        print(
            f"{result['id']}: "
            f"passed={result['passed']} | "
            f"evaluator={result['evaluator_score']:.2f} | "
            f"latency={metadata.get('latency_ms', 0):.0f} ms | "
            f"tokens={metadata.get('total_tokens', 0)} | "
            f"elapsed={elapsed_seconds:.1f}s",
            flush=True,
        )

    total = len(results)

    if total == 0:
        raise RuntimeError(f"No evaluation results produced for {model}.")

    passed = sum(item["passed"] for item in results)

    def average(field: str) -> float:
        return round(
            sum(item[field] for item in results) / total,
            3,
        )

    metadata_results = [
        item["generation_metadata"]
        for item in results
        if item["generation_metadata"] is not None
    ]

    average_latency = (
        round(
            sum(item["latency_ms"] for item in metadata_results)
            / len(metadata_results),
            2,
        )
        if metadata_results
        else None
    )

    total_prompt_tokens = sum(
        item["prompt_tokens"] for item in metadata_results
    )

    total_completion_tokens = sum(
        item["completion_tokens"] for item in metadata_results
    )

    pass_rate = round(passed / total, 3)
    average_evaluator_score = average("evaluator_score")

    release_eligible = (
        pass_rate >= MINIMUM_PASS_RATE
        and average_evaluator_score >= MINIMUM_EVALUATOR_SCORE
        and all(
            item["passed"] and item["evaluator_passed"]
            for item in results
        )
    )

    return {
        "model": model,
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "pass_rate": pass_rate,
        "average_keyword_score": average("keyword_score"),
        "average_source_score": average("source_score"),
        "average_grounding_score": average("grounding_score"),
        "average_completeness_score": average("completeness_score"),
        "average_evaluator_score": average_evaluator_score,
        "average_latency_ms": average_latency,
        "latency_sample_count": len(metadata_results),
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens": total_prompt_tokens + total_completion_tokens,
        "monetary_cost": None,
        "cost_note": "Local Ollama monetary cost is not configured.",
        "release_eligible": release_eligible,
        "cases": results,
    }


def recommend_release(model_results: list[dict]) -> dict:
    eligible = [
        result
        for result in model_results
        if result["release_eligible"]
    ]

    if not eligible:
        return {
            "decision": "NO_RELEASE_CANDIDATE",
            "recommended_model": None,
            "reason": (
                "No model met both the minimum pass rate "
                "and evaluator score thresholds."
            ),
        }

    ranked = sorted(
        eligible,
        key=lambda result: (
            result["pass_rate"],
            result["average_evaluator_score"],
            result["average_latency_ms"] is not None,
            -(
                result["average_latency_ms"]
                if result["average_latency_ms"] is not None
                else 0
            ),
        ),
        reverse=True,
    )

    winner = ranked[0]

    return {
        "decision": "RELEASE_CANDIDATE",
        "recommended_model": winner["model"],
        "reason": (
            "Recommended based on evaluation pass rate, "
            "evaluator score, and latency."
        ),
    }


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare accounting LLM models."
    )

    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help="One or more Ollama model names to evaluate.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Run only the first N test cases.",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        raise ValueError("--limit must be greater than zero.")

    test_cases = load_test_cases()

    dataset_fingerprint = hashlib.sha256(
        TEST_CASES_FILE.read_bytes()
    ).hexdigest()

    if args.limit is not None:
        test_cases = test_cases[:args.limit]

    if not test_cases:
        raise RuntimeError("No evaluation cases were selected.")

    print(
        f"Loaded {len(test_cases)} evaluation cases.",
        flush=True,
    )

    print(
        "\nRetrieving shared evidence for evaluation cases...",
        flush=True,
    )

    evidence_by_case = {}

    for index, test_case in enumerate(test_cases, start=1):
        evidence_by_case[test_case["id"]] = (
            await retrieve_relevant_chunks(
                test_case["question"],
                top_k=5,
            )
        )

        print(
            f"[{index}/{len(test_cases)}] "
            f"{test_case['id']}: "
            f"{len(evidence_by_case[test_case['id']])} chunks retrieved",
            flush=True,
        )

    evidence_manifest = {
        case_id: {
            "fingerprint": calculate_fingerprint(chunks),
            "chunks": chunks,
        }
        for case_id, chunks in evidence_by_case.items()
    }

    model_results = []

    for model in args.models:
        result = await evaluate_model(
            model,
            test_cases,
            evidence_by_case,
        )
        model_results.append(result)

    recommendation = recommend_release(model_results)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset": TEST_CASES_FILE.name,
        "total_cases": len(test_cases),
        "models": model_results,
        "release_recommendation": recommendation,
        "thresholds": {
            "minimum_pass_rate": MINIMUM_PASS_RATE,
            "minimum_evaluator_score": MINIMUM_EVALUATOR_SCORE,
        },
        "dataset_fingerprint": dataset_fingerprint,
        "shared_evidence": evidence_manifest,
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    report_file = RESULTS_DIR / f"comparison_{timestamp}.json"

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print("\n" + "=" * 55)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 55)

    for result in model_results:
        print(
            f"\n{result['model']}"
            f"\n  Pass rate: {result['pass_rate']:.1%}"
            f"\n  Evaluator: {result['average_evaluator_score']:.3f}"
            f"\n  Average latency: {result['average_latency_ms']} ms"
            f"\n  Latency samples: {result['latency_sample_count']}"
            f"\n  Total tokens: {result['total_tokens']}"
            f"\n  Release eligible: {result['release_eligible']}"
        )

    print("\nRelease recommendation:")
    print(json.dumps(recommendation, indent=2))
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())

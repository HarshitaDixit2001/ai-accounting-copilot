from evals.run_evaluation import (
    keyword_match_score,
    source_match_score,
    grounding_score,
    response_completeness_score,
)
import json

from evals.run_evaluation import load_test_cases
from evals.run_comparison import calculate_fingerprint
from evals.run_comparison import recommend_release

def test_keyword_match_score_full_match():
    response = "A journal entry contains a debit and a credit."
    keywords = ["debit", "credit"]

    assert keyword_match_score(response, keywords) == 1.0


def test_keyword_match_score_partial_match():
    response = "A journal entry contains a debit."
    keywords = ["debit", "credit"]

    assert keyword_match_score(response, keywords) == 0.5


def test_keyword_match_score_empty_keywords():
    assert keyword_match_score("Any response", []) == 1.0


def test_source_match_score_expected_source_found():
    sources = [
        {"source": "journal_entries.txt"},
        {"source": "accounting_basics.txt"},
    ]

    assert source_match_score(
        sources,
        ["journal_entries.txt"],
    ) == 1.0


def test_source_match_score_expected_source_missing():
    sources = [
        {"source": "journal_entries.txt"},
    ]

    assert source_match_score(
        sources,
        ["accounting_basics.txt"],
    ) == 0.0


def test_grounding_score_uses_retrieved_evidence():
    response = (
        "A debit increases asset accounts "
        "and a credit increases liability accounts."
    )

    sources = [
        {
            "source": "accounting_basics.txt",
            "content": (
                "A debit increases asset accounts. "
                "A credit increases liability accounts."
            ),
        }
    ]

    score = grounding_score(response, sources)

    assert score > 0.0


def test_response_completeness_score_long_response():
    response = (
        "A journal entry records the financial effect "
        "of a transaction using debit and credit accounts. "
        "It helps maintain accurate financial records "
        "and supports the double-entry accounting system."
    )

    assert response_completeness_score(response) == 1.0


def test_response_completeness_score_medium_response():
    response = (
        "A debit increases an asset account "
        "and decreases a liability account."
    )

    assert response_completeness_score(response) == 0.5


def test_response_completeness_score_short_response():
    response = "Debit"

    assert response_completeness_score(response) == 0.0


def test_response_completeness_score_empty_response():
    assert response_completeness_score("") == 0.0

def test_fingerprint_is_deterministic():
    data = {
        "source": "journal_entries.txt",
        "chunk_id": "chunk_001",
        "content": "A journal entry records a transaction.",
    }

    assert calculate_fingerprint(data) == calculate_fingerprint(data)


def test_fingerprint_is_independent_of_dictionary_key_order():
    first = {
        "source": "journal_entries.txt",
        "chunk_id": "chunk_001",
    }

    second = {
        "chunk_id": "chunk_001",
        "source": "journal_entries.txt",
    }

    assert calculate_fingerprint(first) == calculate_fingerprint(second)


def test_fingerprint_changes_when_evidence_changes():
    original = {
        "source": "journal_entries.txt",
        "content": "A debit increases assets.",
    }

    modified = {
        "source": "journal_entries.txt",
        "content": "A credit increases liabilities.",
    }

    assert calculate_fingerprint(original) != calculate_fingerprint(modified)

def test_recommend_release_prefers_model_with_measured_latency():
    model_results = [
    {
        "model": "model_without_latency",
        "release_eligible": True,
        "pass_rate": 1.0,
        "average_evaluator_score": 1.0,
        "average_latency_ms": None,
    },
    {
        "model": "model_with_latency",
        "release_eligible": True,
        "pass_rate": 1.0,
        "average_evaluator_score": 1.0,
        "average_latency_ms": 5000.0,
    },
    ]
    recommendation = recommend_release(model_results)
    assert recommendation["recommended_model"] == "model_with_latency"

def test_recommend_release_prefers_lower_latency_when_quality_is_equal():
    model_results = [
        {
            "model": "slower_model",
            "release_eligible": True,
            "pass_rate": 1.0,
            "average_evaluator_score": 1.0,
            "average_latency_ms": 5000.0,
        },
        {
            "model": "faster_model",
            "release_eligible": True,
            "pass_rate": 1.0,
            "average_evaluator_score": 1.0,
            "average_latency_ms": 2000.0,
        },
    ]

    recommendation = recommend_release(model_results)

    assert recommendation["recommended_model"] == "faster_model"

def test_recommend_release_excludes_ineligible_model():
    model_results = [
        {
            "model": "high_scoring_but_ineligible",
            "release_eligible": False,
            "pass_rate": 1.0,
            "average_evaluator_score": 1.0,
            "average_latency_ms": 1000.0,
        },
        {
            "model": "eligible_model",
            "release_eligible": True,
            "pass_rate": 0.9,
            "average_evaluator_score": 0.9,
            "average_latency_ms": 3000.0,
        },
    ]

    recommendation = recommend_release(model_results)

    assert recommendation["recommended_model"] == "eligible_model"
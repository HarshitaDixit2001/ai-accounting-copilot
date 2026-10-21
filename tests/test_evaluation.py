from evals.run_evaluation import (
    keyword_match_score,
    source_match_score,
    grounding_score,
    response_completeness_score,
)
import json

from evals.run_evaluation import load_test_cases

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
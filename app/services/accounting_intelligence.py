import re

from app.models.accounting_result import (
    AccountingResult,
    JournalEntry,
    JournalEntryLine,
)
from app.services.rag_service import ask_rag_assistant


def calculate_retrieval_confidence(sources: list[dict]) -> float:
    """
    Convert the strongest retrieval similarity into a bounded
    confidence signal for the API response.
    """
    if not sources:
        return 0.0

    strongest_similarity = max(
        source["similarity"]
        for source in sources
    )

    return round(
        max(0.0, min(strongest_similarity, 1.0)),
        3,
    )


def extract_amount(description: str) -> float:
    """
    Extract a monetary amount from a transaction description.
    Supports values such as:
    ₹25,000
    Rs. 25000
    INR 25000
    25000
    """
    amount_match = re.search(
        r"(?:₹|rs\.?|inr)?\s*(\d+(?:,\d{3})*(?:\.\d+)?)",
        description,
        re.IGNORECASE,
    )

    if not amount_match:
        return 0.0

    return float(amount_match.group(1).replace(",", ""))


def classify_transaction(
    description: str,
    amount: float,
) -> JournalEntry | None:
    """
    Apply deterministic accounting rules to classify
    supported transaction descriptions.
    """
    description_lower = description.lower()

    if "rent" in description_lower and "cash" in description_lower:
        return JournalEntry(
            description=description,
            debit=JournalEntryLine(
                account="Rent Expense",
                amount=amount,
            ),
            credit=JournalEntryLine(
                account="Cash",
                amount=amount,
            ),
        )

    return None


async def explain_accounting_concept(question: str) -> dict:
    result = await ask_rag_assistant(question)

    accounting_result = AccountingResult(
        response=result["response"],
        sources=result["sources"],
        confidence=calculate_retrieval_confidence(
            result["sources"]
        ),
    )

    return accounting_result.model_dump()


async def explain_transaction(transaction_description: str) -> dict:
    result = await ask_rag_assistant(transaction_description)

    amount = extract_amount(transaction_description)

    journal_entry = classify_transaction(
        transaction_description,
        amount,
    )

    accounting_result = AccountingResult(
        response=result["response"],
        journal_entry=journal_entry,
        sources=result["sources"],
        confidence=calculate_retrieval_confidence(
            result["sources"]
        ),
    )

    return accounting_result.model_dump()

from pydantic import BaseModel
from typing import Optional


class JournalEntryLine(BaseModel):
    account: str
    amount: float


class JournalEntry(BaseModel):
    description: str
    debit: JournalEntryLine
    credit: JournalEntryLine


class AccountingResult(BaseModel):
    response: str
    journal_entry: Optional[JournalEntry] = None
    sources: list[dict]
    confidence: float
    review_required: bool = False
    review_reason: Optional[str] = None

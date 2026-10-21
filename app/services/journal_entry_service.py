import logging

from sqlalchemy.orm import Session

from app.core.exceptions import (
    InvoiceNotFoundError,
    AccountingValidationError,
)
from app.models.journal_entry import JournalEntry
from app.repositories.journal_entry_repository import (
    create_journal_entry,
    get_all_journal_entries,
    get_entries_by_transaction,
)
from app.repositories.transaction_repository import (
    get_transaction_by_id,
)


logger = logging.getLogger(__name__)


def create_entry(
    db: Session,
    transaction_id: int,
    account_name: str,
    debit: float = 0,
    credit: float = 0,
) -> JournalEntry:

    if debit < 0 or credit < 0:
        raise AccountingValidationError(
            "Debit and credit amounts cannot be negative"
        )

    if debit > 0 and credit > 0:
        raise AccountingValidationError(
            "A journal entry cannot have both debit and credit"
        )

    if debit == 0 and credit == 0:
        raise AccountingValidationError(
            "A journal entry must have either a debit or credit amount"
        )

    transaction = get_transaction_by_id(
        db,
        transaction_id,
    )

    if transaction is None:
        raise InvoiceNotFoundError(
            f"Transaction {transaction_id}"
        )

    logger.info(
        "Creating journal entry for transaction %s",
        transaction_id,
    )

    entry = JournalEntry(
        transaction_id=transaction_id,
        account_name=account_name,
        debit=debit,
        credit=credit,
    )

    saved_entry = create_journal_entry(
        db,
        entry,
    )

    logger.info(
        "Journal entry %s created successfully",
        saved_entry.id,
    )

    return saved_entry


def create_double_entry(
    db: Session,
    transaction_id: int,
    debit_account: str,
    credit_account: str,
    amount: float,
) -> list[JournalEntry]:

    # Rule 1: amount must be positive
    if amount <= 0:
        raise AccountingValidationError(
            "Transaction amount must be greater than zero"
        )

    # Rule 2: accounts must be different
    if debit_account.strip().lower() == credit_account.strip().lower():
        raise AccountingValidationError(
            "Debit account and credit account must be different"
        )

    # Rule 4: transaction must exist
    transaction = get_transaction_by_id(
        db,
        transaction_id,
    )

    if transaction is None:
        raise InvoiceNotFoundError(
            f"Transaction {transaction_id}"
        )

    logger.info(
        "Creating double-entry journal for transaction %s",
        transaction_id,
    )

    debit_entry = JournalEntry(
        transaction_id=transaction_id,
        account_name=debit_account,
        debit=amount,
        credit=0,
    )

    credit_entry = JournalEntry(
        transaction_id=transaction_id,
        account_name=credit_account,
        debit=0,
        credit=amount,
    )

    # Rule 3: debit must equal credit
    total_debit = debit_entry.debit + credit_entry.debit
    total_credit = debit_entry.credit + credit_entry.credit

    if total_debit != total_credit:
        raise AccountingValidationError(
            "Journal entry is not balanced: "
            "total debit must equal total credit"
        )

    saved_debit = create_journal_entry(
        db,
        debit_entry,
    )

    saved_credit = create_journal_entry(
        db,
        credit_entry,
    )

    logger.info(
        "Balanced journal entry created: Debit=%s Credit=%s",
        total_debit,
        total_credit,
    )

    return [
        saved_debit,
        saved_credit,
    ]


def get_transaction_entries(
    db: Session,
    transaction_id: int,
) -> list[JournalEntry]:

    logger.info(
        "Fetching journal entries for transaction %s",
        transaction_id,
    )

    return get_entries_by_transaction(
        db,
        transaction_id,
    )


def get_journal_entries(
    db: Session,
) -> list[JournalEntry]:

    logger.info("Fetching all journal entries")

    return get_all_journal_entries(db)
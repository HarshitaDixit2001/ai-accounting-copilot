import logging

from sqlalchemy.orm import Session

from app.models.transaction import AccountingTransaction
from app.repositories.transaction_repository import (
    create_transaction,
    get_all_transactions,
    get_transaction_by_id,
)


logger = logging.getLogger(__name__)


def process_transaction(
    db: Session,
    transaction_type: str,
    amount: float,
    description: str | None = None,
    reference_number: str | None = None,
) -> AccountingTransaction:

    logger.info(
        "Processing accounting transaction of type %s",
        transaction_type,
    )

    transaction = AccountingTransaction(
        transaction_type=transaction_type,
        amount=amount,
        description=description,
        reference_number=reference_number,
    )

    saved_transaction = create_transaction(
        db,
        transaction,
    )

    logger.info(
        "Transaction %s saved successfully",
        saved_transaction.id,
    )

    return saved_transaction


def get_transaction(
    db: Session,
    transaction_id: int,
) -> AccountingTransaction | None:

    logger.info(
        "Fetching transaction with ID %s",
        transaction_id,
    )

    return get_transaction_by_id(
        db,
        transaction_id,
    )


def get_transactions(
    db: Session,
) -> list[AccountingTransaction]:

    logger.info("Fetching all accounting transactions")

    return get_all_transactions(db)
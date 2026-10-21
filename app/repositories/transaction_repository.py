from sqlalchemy.orm import Session

from app.models.transaction import AccountingTransaction


def create_transaction(
    db: Session,
    transaction: AccountingTransaction,
) -> AccountingTransaction:
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def get_transaction_by_id(
    db: Session,
    transaction_id: int,
) -> AccountingTransaction | None:
    return (
        db.query(AccountingTransaction)
        .filter(AccountingTransaction.id == transaction_id)
        .first()
    )


def get_all_transactions(
    db: Session,
) -> list[AccountingTransaction]:
    return db.query(AccountingTransaction).all()
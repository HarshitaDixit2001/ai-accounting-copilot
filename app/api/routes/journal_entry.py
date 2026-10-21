from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.journal_entry_service import (
    create_double_entry,
    get_journal_entries,
    get_transaction_entries,
)


router = APIRouter()


@router.post("/journal-entries")
def create_journal_entry(
    transaction_id: int,
    debit_account: str,
    credit_account: str,
    amount: float,
    db: Session = Depends(get_db),
):
    entries = create_double_entry(
        db,
        transaction_id=transaction_id,
        debit_account=debit_account,
        credit_account=credit_account,
        amount=amount,
    )

    return {
        "message": "Balanced journal entry created successfully",
        "entries": [
            {
                "id": entry.id,
                "transaction_id": entry.transaction_id,
                "account_name": entry.account_name,
                "debit": entry.debit,
                "credit": entry.credit,
                "created_at": entry.created_at,
            }
            for entry in entries
        ],
    }


@router.get("/journal-entries")
def read_journal_entries(
    db: Session = Depends(get_db),
):
    entries = get_journal_entries(db)

    return {
        "count": len(entries),
        "entries": [
            {
                "id": entry.id,
                "transaction_id": entry.transaction_id,
                "account_name": entry.account_name,
                "debit": entry.debit,
                "credit": entry.credit,
                "created_at": entry.created_at,
            }
            for entry in entries
        ],
    }


@router.get("/transactions/{transaction_id}/journal-entries")
def read_transaction_journal_entries(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    entries = get_transaction_entries(
        db,
        transaction_id,
    )

    return {
        "transaction_id": transaction_id,
        "count": len(entries),
        "entries": [
            {
                "id": entry.id,
                "transaction_id": entry.transaction_id,
                "account_name": entry.account_name,
                "debit": entry.debit,
                "credit": entry.credit,
                "created_at": entry.created_at,
            }
            for entry in entries
        ],
    }
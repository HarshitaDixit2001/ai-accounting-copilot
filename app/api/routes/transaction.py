from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.accounting import TransactionRequest
from app.services.transaction_service import (
    process_transaction,
    get_transaction,
    get_transactions,
)


router = APIRouter()


@router.post("/transactions")
def create_transaction(
    transaction: TransactionRequest,
    db: Session = Depends(get_db),
):
    saved_transaction = process_transaction(
        db,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        reference_number=transaction.reference_number,
    )

    return {
        "message": "Transaction created successfully",
        "transaction": {
            "id": saved_transaction.id,
            "transaction_type": saved_transaction.transaction_type,
            "amount": saved_transaction.amount,
            "description": saved_transaction.description,
            "reference_number": saved_transaction.reference_number,
            "created_at": saved_transaction.created_at,
        },
    }


@router.get("/transactions")
def read_transactions(
    db: Session = Depends(get_db),
):
    transactions = get_transactions(db)

    return {
        "count": len(transactions),
        "transactions": [
            {
                "id": transaction.id,
                "transaction_type": transaction.transaction_type,
                "amount": transaction.amount,
                "description": transaction.description,
                "reference_number": transaction.reference_number,
                "created_at": transaction.created_at,
            }
            for transaction in transactions
        ],
    }


@router.get("/transactions/{transaction_id}")
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    transaction = get_transaction(
        db,
        transaction_id,
    )

    if transaction is None:
        return {
            "message": "Transaction not found",
            "transaction_id": transaction_id,
        }

    return {
        "transaction": {
            "id": transaction.id,
            "transaction_type": transaction.transaction_type,
            "amount": transaction.amount,
            "description": transaction.description,
            "reference_number": transaction.reference_number,
            "created_at": transaction.created_at,
        },
    }
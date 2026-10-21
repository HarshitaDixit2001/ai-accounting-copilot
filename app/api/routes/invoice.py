from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.accounting import InvoiceRequest
from app.services.invoice_service import (
    process_invoice,
    get_invoice,
    get_invoices,
    update_invoice_data,
    remove_invoice,
)


router = APIRouter()


@router.post("/invoices")
def create_invoice(
    invoice: InvoiceRequest,
    db: Session = Depends(get_db),
):
    processed_invoice = process_invoice(
        db,
        invoice,
    )

    return {
        "message": "Invoice created successfully",
        "invoice": {
            "id": processed_invoice.id,
            "invoice_number": processed_invoice.invoice_number,
            "vendor": processed_invoice.vendor,
            "amount": processed_invoice.amount,
            "description": processed_invoice.description,
        },
    }


@router.get("/invoices")
def read_invoices(
    db: Session = Depends(get_db),
):
    invoices = get_invoices(db)

    return {
        "count": len(invoices),
        "invoices": [
            {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "vendor": invoice.vendor,
                "amount": invoice.amount,
                "description": invoice.description,
            }
            for invoice in invoices
        ],
    }


@router.get("/invoices/{invoice_id}")
def read_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    invoice = get_invoice(
        db,
        invoice_id,
    )

    return {
        "invoice": {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "vendor": invoice.vendor,
            "amount": invoice.amount,
            "description": invoice.description,
        },
    }


@router.put("/invoices/{invoice_id}")
def update_invoice(
    invoice_id: int,
    invoice_data: InvoiceRequest,
    db: Session = Depends(get_db),
):
    updated_invoice = update_invoice_data(
        db,
        invoice_id,
        invoice_data,
    )

    return {
        "message": "Invoice updated successfully",
        "invoice": {
            "id": updated_invoice.id,
            "invoice_number": updated_invoice.invoice_number,
            "vendor": updated_invoice.vendor,
            "amount": updated_invoice.amount,
            "description": updated_invoice.description,
        },
    }


@router.delete("/invoices/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
):
    remove_invoice(
        db,
        invoice_id,
    )

    return {
        "message": "Invoice deleted successfully",
        "invoice_id": invoice_id,
    }
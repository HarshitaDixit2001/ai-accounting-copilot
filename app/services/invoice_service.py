import logging

from sqlalchemy.orm import Session

from app.core.exceptions import InvoiceNotFoundError
from app.models.invoice import Invoice
from app.repositories.invoice_repository import (
    create_invoice,
    get_all_invoices,
    get_invoice_by_id,
    update_invoice,
    delete_invoice,
)
from app.schemas.accounting import InvoiceRequest


logger = logging.getLogger(__name__)


def process_invoice(
    db: Session,
    invoice_data: InvoiceRequest,
) -> Invoice:
    logger.info(
        "Processing invoice %s from vendor %s",
        invoice_data.invoice_number,
        invoice_data.vendor,
    )

    invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        vendor=invoice_data.vendor,
        amount=invoice_data.amount,
        description=invoice_data.description,
    )

    saved_invoice = create_invoice(
        db,
        invoice,
    )

    logger.info(
        "Invoice %s saved successfully",
        saved_invoice.invoice_number,
    )

    return saved_invoice


def get_invoice(
    db: Session,
    invoice_id: int,
) -> Invoice:
    logger.info(
        "Fetching invoice with ID %s",
        invoice_id,
    )

    invoice = get_invoice_by_id(
        db,
        invoice_id,
    )

    if invoice is None:
        logger.warning(
            "Invoice with ID %s was not found",
            invoice_id,
        )
        raise InvoiceNotFoundError(str(invoice_id))

    return invoice


def get_invoices(
    db: Session,
) -> list[Invoice]:
    logger.info("Fetching all invoices")

    return get_all_invoices(db)


def update_invoice_data(
    db: Session,
    invoice_id: int,
    invoice_data: InvoiceRequest,
) -> Invoice:
    logger.info(
        "Updating invoice with ID %s",
        invoice_id,
    )

    invoice = get_invoice_by_id(
        db,
        invoice_id,
    )

    if invoice is None:
        logger.warning(
            "Cannot update invoice with ID %s because it was not found",
            invoice_id,
        )
        raise InvoiceNotFoundError(str(invoice_id))

    invoice.invoice_number = invoice_data.invoice_number
    invoice.vendor = invoice_data.vendor
    invoice.amount = invoice_data.amount
    invoice.description = invoice_data.description

    updated_invoice = update_invoice(
        db,
        invoice,
    )

    logger.info(
        "Invoice with ID %s updated successfully",
        invoice_id,
    )

    return updated_invoice


def remove_invoice(
    db: Session,
    invoice_id: int,
) -> None:
    logger.info(
        "Deleting invoice with ID %s",
        invoice_id,
    )

    invoice = get_invoice_by_id(
        db,
        invoice_id,
    )

    if invoice is None:
        logger.warning(
            "Cannot delete invoice with ID %s because it was not found",
            invoice_id,
        )
        raise InvoiceNotFoundError(str(invoice_id))

    delete_invoice(
        db,
        invoice,
    )

    logger.info(
        "Invoice with ID %s deleted successfully",
        invoice_id,
    )
from sqlalchemy.orm import Session

from app.models.invoice import Invoice


def create_invoice(
    db: Session,
    invoice: Invoice,
) -> Invoice:
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice


def get_invoice_by_id(
    db: Session,
    invoice_id: int,
) -> Invoice | None:
    return (
        db.query(Invoice)
        .filter(Invoice.id == invoice_id)
        .first()
    )


def get_all_invoices(
    db: Session,
) -> list[Invoice]:
    return db.query(Invoice).all()


def update_invoice(
    db: Session,
    invoice: Invoice,
) -> Invoice:
    db.commit()
    db.refresh(invoice)

    return invoice


def delete_invoice(
    db: Session,
    invoice: Invoice,
) -> None:
    db.delete(invoice)
    db.commit()
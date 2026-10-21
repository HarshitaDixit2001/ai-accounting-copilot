from sqlalchemy import Column, Float, Integer, String, Text

from app.db.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    vendor = Column(
        String(255),
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )
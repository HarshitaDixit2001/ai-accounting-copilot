from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.database import Base


class AccountingTransaction(Base):
    __tablename__ = "accounting_transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    transaction_type = Column(
        String(50),
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

    reference_number = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
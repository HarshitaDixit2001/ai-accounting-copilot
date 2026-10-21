from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.database import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    transaction_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    account_name = Column(
        String(255),
        nullable=False,
    )

    debit = Column(
        Float,
        default=0,
        nullable=False,
    )

    credit = Column(
        Float,
        default=0,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
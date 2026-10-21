from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class AIAuditLog(Base):
    __tablename__ = "ai_audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    request_id = Column(
        String(100),
        nullable=False,
        index=True,
    )

    question = Column(
        Text,
        nullable=False,
    )

    response = Column(
        Text,
        nullable=False,
    )

    sources = Column(
        Text,
        nullable=True,
    )

    evaluator_score = Column(
        String(20),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
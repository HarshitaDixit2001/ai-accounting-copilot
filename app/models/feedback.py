from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), nullable=False, index=True)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
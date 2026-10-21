from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.request_context import get_request_id
from app.db.database import get_db
from app.models import feedback
from app.models.feedback import AIFeedback
from app.core.metrics import record_feedback

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
)


class FeedbackRequest(BaseModel):
    request_id: str = Field(min_length=1, max_length=100)
    rating: int = Field(ge=0, le=1)
    feedback: str | None = Field(default=None, max_length=2000)


@router.post("")
def submit_feedback(
    feedback_request: FeedbackRequest,
    db: Session = Depends(get_db),
):
    feedback = AIFeedback(
        request_id=feedback_request.request_id,
        rating=feedback_request.rating,
        feedback=feedback_request.feedback,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    record_feedback(feedback.rating)
    return {
        "status": "recorded",
        "feedback_id": feedback.id,
        "request_id": feedback.request_id,
    }
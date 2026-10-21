from pydantic import BaseModel, Field


class TransactionExplanationRequest(BaseModel):
    description: str = Field(..., min_length=1)
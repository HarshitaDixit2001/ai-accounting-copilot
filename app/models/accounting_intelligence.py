from pydantic import BaseModel, Field


class AccountingIntelligenceRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
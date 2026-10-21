from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=5000)


class LLMResponse(BaseModel):
    response: str


class AccountingResponse(BaseModel):
    answer: str
    debit_account: str | None = None
    credit_account: str | None = None
    amount: float | None = None

class RAGSource(BaseModel):
    source: str
    chunk_id: int
    similarity: float

class RAGResponse(BaseModel):
    response: str
    sources: list[RAGSource]
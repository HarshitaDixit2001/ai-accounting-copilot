from pydantic import BaseModel, Field


class InvoiceRequest(BaseModel):
    invoice_number: str
    vendor: str
    amount: float = Field(gt=0)
    description: str | None = None

class TransactionRequest(BaseModel):
    transaction_type: str
    amount: float = Field(gt=0)
    description: str | None = None
    reference_number: str | None = None
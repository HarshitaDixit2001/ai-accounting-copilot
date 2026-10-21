from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.request_context import get_request_id
from app.db.database import get_db
from app.models.accounting_intelligence import AccountingIntelligenceRequest
from app.models.transaction_explanation import TransactionExplanationRequest
from app.services.accounting_intelligence import (
    explain_accounting_concept,
    explain_transaction,
)
from app.services.audit_service import record_ai_audit
from app.services.evaluator import evaluate_accounting_response
from app.core.metrics import record_business_outcome

router = APIRouter(
    prefix="/accounting",
    tags=["Accounting"],
)


@router.post("/intelligence")
async def accounting_intelligence(
    request: AccountingIntelligenceRequest,
    db: Session = Depends(get_db),
):
    result = await explain_accounting_concept(request.prompt)

    evaluation = evaluate_accounting_response(
        question=request.prompt,
        response=result["response"],
        sources=result["sources"],
    )
    record_business_outcome(
        abstained=evaluation["evaluation_type"] == "abstention",
        transaction_explanation=True,
    )
    record_ai_audit(
        db=db,
        request_id=get_request_id(),
        question=request.prompt,
        response=result["response"],
        sources=result["sources"],
        evaluator_score=evaluation["score"],
    )

    return result


@router.post("/transaction/explain")
async def transaction_explanation(
    request: TransactionExplanationRequest,
    db: Session = Depends(get_db),
):
    result = await explain_transaction(request.description)

    evaluation = evaluate_accounting_response(
        question=request.description,
        response=result["response"],
        sources=result["sources"],
    )
    record_business_outcome(
        abstained=evaluation["evaluation_type"] == "abstention",
        transaction_explanation=True,
    )
    record_ai_audit(
        db=db,
        request_id=get_request_id(),
        question=request.description,
        response=result["response"],
        sources=result["sources"],
        evaluator_score=evaluation["score"],
    )
    
    return result
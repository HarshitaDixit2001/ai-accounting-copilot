from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    InvoiceNotFoundError,
    AccountingValidationError,
    OllamaServiceError,
)
from app.core.request_context import get_request_id


async def invoice_not_found_handler(
    request: Request,
    exc: InvoiceNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={
            "error": "invoice_not_found",
            "message": str(exc),
            "invoice_number": exc.invoice_number,
            "request_id": get_request_id(),
        },
    )


async def accounting_validation_handler(
    request: Request,
    exc: AccountingValidationError,
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "accounting_validation_error",
            "message": exc.message,
            "request_id": get_request_id(),
        },
    )


async def ollama_service_error_handler(
    request: Request,
    exc: OllamaServiceError,
):
    return JSONResponse(
        status_code=503,
        content={
            "error": "ollama_service_unavailable",
            "message": exc.message,
            "request_id": get_request_id(),
        },
    )
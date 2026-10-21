import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import accounting
from app.api.routes.health import router as health_router
from app.api.routes.invoice import router as invoice_router
from app.api.routes.transaction import router as transaction_router
from app.api.routes.journal_entry import router as journal_entry_router
from app.api.routes.llm import router as llm_router
from app.api.routes.metrics import router as metrics_router

from app.core.config import settings
from app.core.exception_handlers import (
    accounting_validation_handler,
    invoice_not_found_handler,
    ollama_service_error_handler,
)
from app.core.exceptions import (
    AccountingValidationError,
    InvoiceNotFoundError,
    OllamaServiceError,
)
from app.core.logging_config import setup_logging
from app.core.request_context import get_request_id
from app.core.request_middleware import RequestLoggingMiddleware

from app.db.database import Base, engine

from app.models.invoice import Invoice
from app.models.transaction import AccountingTransaction
from app.models.journal_entry import JournalEntry
from app.models.feedback import AIFeedback
from app.api.routes.feedback import router as feedback_router
from app.models.ai_audit import AIAuditLog
from app.api.routes.audit import router as audit_router
from fastapi.middleware.cors import CORSMiddleware
setup_logging()

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI platform for accounting assistance",
    version=settings.APP_VERSION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)


async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = get_request_id()

    logger.exception(
        "Unhandled application exception | request_id=%s | path=%s",
        request_id,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected internal error occurred.",
            "request_id": request_id,
        },
    )


app.add_exception_handler(
    InvoiceNotFoundError,
    invoice_not_found_handler,
)

app.add_exception_handler(
    AccountingValidationError,
    accounting_validation_handler,
)

app.add_exception_handler(
    OllamaServiceError,
    ollama_service_error_handler,
)

app.add_exception_handler(
    Exception,
    global_exception_handler,
)


app.include_router(health_router)
app.include_router(invoice_router)
app.include_router(transaction_router)
app.include_router(journal_entry_router)
app.include_router(llm_router)
app.include_router(accounting.router)
app.include_router(metrics_router)
app.include_router(feedback_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
from fastapi import APIRouter

from app.schemas.llm import (
    LLMRequest,
    LLMResponse,
    AccountingResponse,
    RAGResponse,
)

from app.services.ollama_service import generate_response
from app.services.accounting_service import ask_accounting_assistant
from app.services.rag_service import ask_rag_assistant
from app.rag.retriever import build_knowledge_index


router = APIRouter()


@router.post(
    "/llm/generate",
    response_model=LLMResponse,
)
async def generate_llm_response(request: LLMRequest):
    response = await generate_response(
        request.prompt
    )

    return LLMResponse(
        response=response
    )


@router.post(
    "/accounting/ask",
    response_model=AccountingResponse,
)
async def ask_accounting(request: LLMRequest):
    response = await ask_accounting_assistant(
        request.prompt
    )

    return response


@router.post(
    "/accounting/rag",
    response_model=RAGResponse,
)
async def ask_rag(request: LLMRequest):
    response = await ask_rag_assistant(
        request.prompt
    )

    return response


@router.post(
    "/accounting/rag/index"
)
async def build_rag_index():
    indexed_count = await build_knowledge_index()

    return {
        "message": "Knowledge index built successfully",
        "indexed_chunks": indexed_count,
    }
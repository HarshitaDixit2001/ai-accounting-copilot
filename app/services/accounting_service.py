from app.prompts.accounting import build_accounting_prompt
from app.services.ollama_service import generate_response
from app.schemas.llm import AccountingResponse


async def ask_accounting_assistant(question: str) -> AccountingResponse:
    prompt = build_accounting_prompt(question)

    response = await generate_response(prompt)

    return AccountingResponse(
        answer=response,
    )
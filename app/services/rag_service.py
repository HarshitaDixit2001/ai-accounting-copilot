import logging
import time

from app.core.metrics import record_rag_request
from app.prompts.rag import build_rag_prompt
from app.rag.retriever import retrieve_relevant_chunks
from app.services.ollama_service import generate_response


logger = logging.getLogger(__name__)


def has_sufficient_evidence(
    question: str,
    chunks: list[dict],
) -> bool:
    """
    Check whether the retrieved evidence contains
    meaningful terms from the user's question.
    """
    if not chunks:
        return False

    stop_terms = {
        "accounting",
        "company",
        "complex",
        "treatment",
        "account",
        "should",
        "what",
        "does",
        "how",
        "for",
        "the",
        "and",
        "with",
        "paid",
    }

    question_terms = {
        term.strip(".,:;()[]?'\"₹").lower()
        for term in question.split()
        if (
            len(term.strip(".,:;()[]?'\"₹")) >= 4
            and term.strip(".,:;()[]?'\"₹").lower()
            not in stop_terms
            and not term.strip(
                ".,:;()[]?'\"₹"
            ).replace(",", "").replace(".", "").isdigit()
        )
    }

    if not question_terms:
        return False

    evidence_text = " ".join(
        chunk["content"]
        for chunk in chunks
    ).lower()

    matched_terms = [
        term
        for term in question_terms
        if term in evidence_text
    ]

    logger.info(
        "RAG evidence gate | question_terms=%s | matched_terms=%s",
        sorted(question_terms),
        sorted(matched_terms),
    )

    return len(matched_terms) >= 1


async def ask_rag_assistant(
    question: str,
) -> dict:
    pipeline_start = time.perf_counter()

    retrieval_start = time.perf_counter()

    relevant_chunks = await retrieve_relevant_chunks(
        question,
        top_k=5,
    )

    retrieval_duration_ms = (
        time.perf_counter() - retrieval_start
    ) * 1000

    logger.info(
        "RAG pipeline retrieval | duration_ms=%.2f | chunks=%s",
        retrieval_duration_ms,
        len(relevant_chunks),
    )

    if not has_sufficient_evidence(
        question,
        relevant_chunks,
    ):
        pipeline_duration_ms = (
            time.perf_counter() - pipeline_start
        ) * 1000

        record_rag_request(
            retrieval_duration_ms=retrieval_duration_ms,
            llm_duration_ms=0.0,
            abstained=True,
        )

        logger.info(
            "RAG pipeline abstained | duration_ms=%.2f | "
            "chunks=%s | reason=evidence_insufficient",
            pipeline_duration_ms,
            len(relevant_chunks),
        )

        return {
            "response": (
                "The provided accounting knowledge "
                "does not contain enough information "
                "to answer this question."
            ),
            "sources": [],
        }

    context = "\n\n".join(
        (
            f"Source: {chunk['source']}\n"
            f"Chunk ID: {chunk['chunk_id']}\n"
            f"Content:\n{chunk['content']}"
        )
        for chunk in relevant_chunks
    )

    prompt = build_rag_prompt(
        question=question,
        context=context,
    )

    llm_start = time.perf_counter()

    response = await generate_response(prompt)

    llm_duration_ms = (
        time.perf_counter() - llm_start
    ) * 1000

    logger.info(
        "RAG pipeline LLM generation | duration_ms=%.2f",
        llm_duration_ms,
    )

    record_rag_request(
        retrieval_duration_ms=retrieval_duration_ms,
        llm_duration_ms=llm_duration_ms,
        abstained=False,
    )

    sources = [
        {
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
            "similarity": chunk["similarity"],
            "content": chunk["content"],
        }
        for chunk in relevant_chunks
    ]

    pipeline_duration_ms = (
        time.perf_counter() - pipeline_start
    ) * 1000

    logger.info(
        "RAG pipeline completed | duration_ms=%.2f | sources=%s",
        pipeline_duration_ms,
        len(sources),
    )

    return {
        "response": response,
        "sources": sources,
    }
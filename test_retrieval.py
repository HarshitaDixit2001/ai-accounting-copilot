import asyncio

from app.rag.retriever import retrieve_relevant_chunks


async def main():
    results = await retrieve_relevant_chunks(
        "How do I record rent paid in cash?",
        top_k=5,
    )

    print(f"\nRetrieved chunks: {len(results)}")

    for result in results:
        print(
            f"\n--- {result['source']} "
            f"| similarity={result['similarity']:.4f} ---"
        )
        print(result["content"])


asyncio.run(main())
from pathlib import Path

from app.rag.chunker import chunk_text


DOCUMENTS_PATH = Path("knowledge_base/documents")


def load_documents() -> list[dict]:
    documents = []

    for file_path in DOCUMENTS_PATH.glob("*.txt"):
        content = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        documents.append(
            {
                "source": file_path.name,
                "content": content,
            }
        )

    return documents


def load_and_chunk_documents() -> list[dict]:
    chunks = []

    documents = load_documents()

    for document in documents:
        document_chunks = chunk_text(
            document["content"]
        )

        for index, chunk in enumerate(document_chunks):
            chunks.append(
                {
                    "source": document["source"],
                    "chunk_id": index,
                    "content": chunk,
                }
            )

    return chunks
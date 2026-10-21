from app.rag.loader import load_documents


def test_load_documents():
    documents = load_documents()

    assert len(documents) == 3

    sources = {
        document["source"]
        for document in documents
    }

    assert "journal_entries.txt" in sources
    assert "accounting_basics.txt" in sources
    assert "financial_transactions.txt" in sources


def test_loaded_documents_have_content():
    documents = load_documents()

    for document in documents:
        assert document["source"]
        assert document["content"]
        assert len(document["content"]) > 50

def test_load_and_chunk_documents():
    from app.rag.loader import load_and_chunk_documents

    chunks = load_and_chunk_documents()

    assert chunks

    for chunk in chunks:
        assert chunk["source"]
        assert isinstance(chunk["chunk_id"], int)
        assert chunk["content"]
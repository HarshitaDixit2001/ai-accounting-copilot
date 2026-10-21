import pytest

from app.rag.chunker import chunk_text


def test_chunk_text():
    text = "A" * 1200

    chunks = chunk_text(
        text,
        chunk_size=500,
        overlap=50,
    )

    assert len(chunks) == 3

    assert len(chunks[0]) == 500
    assert len(chunks[1]) == 500
    assert len(chunks[2]) == 300


def test_chunks_have_overlap():
    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = chunk_text(
        text,
        chunk_size=10,
        overlap=3,
    )

    assert chunks[0][-3:] == chunks[1][:3]


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "Some accounting text",
            chunk_size=100,
            overlap=100,
        )
from pathlib import Path

import pytest

from src.chunking.structure_aware import create_chunks
from src.ingestion.loader import load_legislation
from src.retrieval.bm25 import BM25Retriever


FIXTURE_PATH = Path("data/fixtures/sample_act.xml")


@pytest.fixture
def retriever():
    sections = load_legislation(FIXTURE_PATH)
    chunks = create_chunks(sections)

    return BM25Retriever(chunks)


def test_retriever_returns_results(retriever):
    results = retriever.search(
        "What is the purpose of this Act?",
        top_k=2,
    )

    assert len(results) == 2


def test_retriever_returns_relevant_section(retriever):
    results = retriever.search(
        "What is the purpose of this Act?",
        top_k=1,
    )

    assert results[0].chunk.section_number == "1"
    assert results[0].chunk.section_heading == "Purpose"


def test_retrieval_results_have_scores(retriever):
    results = retriever.search(
        "public organisations",
        top_k=2,
    )

    for result in results:
        assert isinstance(result.score, float)


def test_empty_query_is_rejected(retriever):
    with pytest.raises(ValueError):
        retriever.search("")


def test_invalid_top_k_is_rejected(retriever):
    with pytest.raises(ValueError):
        retriever.search("public organisations", top_k=0)


def test_empty_chunks_are_rejected():
    with pytest.raises(ValueError):
        BM25Retriever([])
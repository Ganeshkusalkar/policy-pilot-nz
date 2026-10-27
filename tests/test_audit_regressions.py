import os
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.retrieval.bm25 import tokenize, BM25Index
from app.services.qa_service import (
    filter_citations_by_answer,
    normalize_section_label,
    get_documents,
)


client = TestClient(app)


def test_ask_rejects_whitespace_only_question():
    """Ensure whitespace-only questions are rejected with HTTP 422."""
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("question" in err["loc"] for err in errors)


def test_ask_rejects_sub_minimum_stripped_question():
    """Ensure questions whose stripped content is < 3 chars are rejected with HTTP 422."""
    response = client.post("/ask", json={"question": "  hi  "})
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("question" in err["loc"] for err in errors)


def test_normalize_section_label_clean_various_formats():
    """Verify that section label prefixes, abbreviations, and punctuation are normalized."""
    assert normalize_section_label("Section 22") == "22"
    assert normalize_section_label("section 22") == "22"
    assert normalize_section_label("s. 23") == "23"
    assert normalize_section_label("s 23.") == "23"
    assert normalize_section_label(" 14, ") == "14"


def test_filter_citations_handles_natural_language_section_lists():
    """Verify that valid natural language section listings from Gemini are accepted."""
    retrieved = [
        {"label": "22", "heading": "Liberty of the person", "source_url": "https://example.com/22"},
        {"label": "23", "heading": "Rights of persons arrested or detained", "source_url": "https://example.com/23"},
    ]
    raw_answer = (
        "Everyone has the right not to be arbitrarily arrested or detained (section 22). "
        "Persons arrested have specific rights to consult a lawyer (section 23).\n\n"
        "Supporting sections: Section 22 and Section 23."
    )
    cleaned_answer, citations, abstained = filter_citations_by_answer(raw_answer, retrieved)

    assert not abstained
    assert len(citations) == 2
    cited_sections = {c["section"] for c in citations}
    assert cited_sections == {"22", "23"}
    assert "Supporting sections" not in cleaned_answer


def test_filter_citations_rejects_hallucinated_sections():
    """Ensure hallucinated sections not in retrieved evidence cause abstention."""
    retrieved = [
        {"label": "14", "heading": "Freedom of expression", "source_url": "https://example.com/14"},
    ]
    raw_answer = "Freedom of speech is guaranteed.\n\nSupporting sections: 14, 999"
    cleaned_answer, citations, abstained = filter_citations_by_answer(raw_answer, retrieved)

    assert abstained
    assert citations == []


def test_bm25_tokenize_normalizes_maori_macrons():
    """Verify that Māori macrons (ā, ē, ī, ō, ū) normalize to ascii base characters."""
    assert tokenize("Māori") == tokenize("Maori")
    assert tokenize("whānau") == ["whanau"]
    assert tokenize("kāwanatanga") == ["kawanatanga"]


def test_bm25_retrieves_section_16_for_protest_synonyms():
    """Verify that civil liberty synonyms like protest/demonstrate retrieve Section 16."""
    documents = [
        {"label": "16", "heading": "Freedom of peaceful assembly", "text": "Everyone has the right to freedom of peaceful assembly."},
        {"label": "14", "heading": "Freedom of expression", "text": "Everyone has the right to freedom of expression."},
        {"label": "21", "heading": "Unreasonable search", "text": "Everyone has the right to be secure against unreasonable search."},
    ]
    index = BM25Index(documents)
    results = index.search("Can citizens demonstrate and protest peacefully?", top_k=1)
    assert len(results) == 1
    assert results[0]["label"] == "16"


def test_get_documents_resilient_to_working_directory(tmp_path):
    """Verify that get_documents loads the corpus even if the process working directory is changed."""
    original_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        documents = get_documents()
        assert len(documents) > 0
        assert any(d.get("label") == "1" for d in documents)
    finally:
        os.chdir(original_cwd)


def test_ask_endpoint_handles_unexpected_exceptions_safely():
    """Verify that internal unexpected exceptions return 500 without leaking stack traces."""
    with patch("app.api.ask.answer_question", side_effect=ValueError("Internal sensitive DB string")):
        response = client.post("/ask", json={"question": "What is freedom of speech?"})
        assert response.status_code == 500
        assert response.json() == {
            "detail": "An unexpected error occurred while processing your request."
        }
        assert "Internal sensitive DB string" not in response.text

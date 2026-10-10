
from app.retrieval.bm25 import BM25Index, tokenize


def sample_documents():
    return [
        {
            "chunk_id": "act:1:1",
            "text": (
                "This Act may be cited as the New Zealand "
                "Bill of Rights Act 1990."
            ),
            "search_text": "1 Short Title This Act may be cited as the New Zealand Bill of Rights Act 1990.",
            "provision_type": "prov",
            "provision_id": "act:1",
            "label": "1",
            "heading": "Short Title",
            "chunk_index": 0,
            "source_title": "New Zealand Bill of Rights Act 1990",
            "work_id": "test-work",
            "version_id": "test-version",
            "source_url": "https://example.org/act.xml",
        },
        {
            "chunk_id": "act:2:1",
            "text": (
                "The rights and freedoms contained in this Bill "
                "of Rights are affirmed."
            ),
            "search_text": (
                "2 Rights affirmed The rights and freedoms "
                "contained in this Bill of Rights are affirmed."
            ),
            "provision_type": "prov",
            "provision_id": "act:2",
            "label": "2",
            "heading": "Rights affirmed",
            "chunk_index": 0,
            "source_title": "New Zealand Bill of Rights Act 1990",
            "work_id": "test-work",
            "version_id": "test-version",
            "source_url": "https://example.org/act.xml",
        },
        {
            "chunk_id": "act:3:1",
            "text": (
                "This Bill of Rights applies to acts done by the "
                "legislative, executive, or judicial branches of "
                "the Government of New Zealand."
            ),
            "search_text": (
                "3 Application This Bill of Rights applies to acts "
                "done by the legislative, executive, or judicial "
                "branches of the Government of New Zealand."
            ),
            "provision_type": "prov",
            "provision_id": "act:3",
            "label": "3",
            "heading": "Application",
            "chunk_index": 0,
            "source_title": "New Zealand Bill of Rights Act 1990",
            "work_id": "test-work",
            "version_id": "test-version",
            "source_url": "https://example.org/act.xml",
        },
    ]


def test_tokenize_normalizes_text():
    assert tokenize("Rights & FREEDOMS, 1990!") == [
        "right",
        "freedom",
        "1990",
    ]


def test_search_ranks_relevant_provision_first():
    index = BM25Index(sample_documents())

    results = index.search("rights and freedoms affirmed", top_k=2)

    assert results
    assert results[0]["label"] == "2"
    assert results[0]["heading"] == "Rights affirmed"


def test_search_preserves_source_metadata():
    index = BM25Index(sample_documents())

    results = index.search("Short Title", top_k=1)

    assert results[0]["chunk_id"] == "act:1:1"
    assert results[0]["source_url"] == "https://example.org/act.xml"
    assert results[0]["score"] > 0


def test_search_returns_empty_for_no_matches():
    index = BM25Index(sample_documents())

    assert index.search("volcanic astronomy", top_k=3) == []
    assert index.search("   ", top_k=3) == []


def test_natural_language_questions_rank_relevant_provision():
    index = BM25Index(sample_documents())

    rights_results = index.search(
        "Which rights and freedoms does the Act affirm?",
        top_k=1,
    )
    application_results = index.search(
        "How does the Act apply to government actions?",
        top_k=1,
    )

    assert rights_results[0]["label"] == "2"
    assert application_results[0]["label"] == "3"


def test_legal_synonyms_retrieve_relevant_provision():
    documents = [
        {
            "chunk_id": "act:4:1",
            "text": (
                "No court shall hold any provision of an enactment "
                "invalid or ineffective because it is inconsistent "
                "with any provision of this Bill of Rights."
            ),
            "search_text": (
                "4 Other enactments not affected No court shall hold "
                "any provision of an enactment invalid or ineffective "
                "because it is inconsistent with this Bill of Rights."
            ),
            "label": "4",
            "heading": "Other enactments not affected",
        },
        {
            "chunk_id": "act:7A:1",
            "text": (
                "The Attorney-General must notify Parliament "
                "of a declaration of inconsistency."
            ),
            "search_text": (
                "7A Attorney-General to notify Parliament of "
                "declaration of inconsistency"
            ),
            "label": "7A",
            "heading": (
                "Attorney-General to notify Parliament "
                "of declaration of inconsistency"
            ),
        },
    ]

    index = BM25Index(documents)

    results = index.search(
        "Can a court invalidate an enactment because it conflicts with this Act?",
        top_k=3,
    )

    assert results
    assert results[0]["label"] == "4"


from app.services.qa_service import (
    ABSTENTION,
    filter_citations_by_answer,
)


def make_document(label: str, heading: str) -> dict:
    return {
        "label": label,
        "heading": heading,
        "text": f"Text for section {label}.",
        "source_url": "https://www.legislation.govt.nz/example.xml",
    }


def test_valid_supporting_sections_return_matching_citations():
    retrieved = [
        make_document("22", "Liberty of the person"),
        make_document("23", "Rights of persons arrested or detained"),
        make_document("1", "Short Title and commencement"),
    ]

    answer = (
        "Section 22 protects against arbitrary arrest or detention. "
        "Section 23 provides additional rights.\n"
        "Supporting sections: 22, 23"
    )

    cleaned, citations, abstained = filter_citations_by_answer(
        answer,
        retrieved,
    )

    assert not abstained
    assert "Supporting sections:" not in cleaned
    assert [citation["section"] for citation in citations] == [
        "22",
        "23",
    ]


def test_unknown_section_causes_abstention():
    retrieved = [make_document("22", "Liberty of the person")]

    answer = (
        "Section 22 provides protection.\n"
        "Supporting sections: 22, 99"
    )

    cleaned, citations, abstained = filter_citations_by_answer(
        answer,
        retrieved,
    )

    assert abstained
    assert cleaned == ABSTENTION
    assert citations == []


def test_missing_supporting_sections_line_causes_abstention():
    retrieved = [make_document("22", "Liberty of the person")]

    cleaned, citations, abstained = filter_citations_by_answer(
        "Section 22 provides protection.",
        retrieved,
    )

    assert abstained
    assert cleaned == ABSTENTION
    assert citations == []


def test_none_supporting_sections_causes_abstention():
    retrieved = [make_document("22", "Liberty of the person")]

    cleaned, citations, abstained = filter_citations_by_answer(
        "The evidence is insufficient.\nSupporting sections: none",
        retrieved,
    )

    assert abstained
    assert cleaned == ABSTENTION
    assert citations == []


from pathlib import Path

import pytest

from src.chunking.structure_aware import create_chunks
from src.ingestion.loader import load_legislation


FIXTURE_PATH = Path("data/fixtures/sample_act.xml")


def test_create_chunks():
    sections = load_legislation(FIXTURE_PATH)
    chunks = create_chunks(sections)

    assert len(chunks) == 3


def test_chunk_preserves_structure():
    sections = load_legislation(FIXTURE_PATH)
    chunks = create_chunks(sections)

    first = chunks[0]

    assert first.chunk_id == (
        "sample_act_1990_001:part-1:section-1:chunk-1"
    )
    assert first.part_number == "1"
    assert first.part_title == "Preliminary"
    assert first.section_number == "1"
    assert first.section_heading == "Purpose"


def test_chunk_preserves_source():
    sections = load_legislation(FIXTURE_PATH)
    chunks = create_chunks(sections)

    for chunk in chunks:
        assert chunk.source_url == "https://example.govt.nz/sample-act"
        assert chunk.work_id == "sample_act_1990_001"
        assert chunk.text


def test_large_section_is_split():
    sections = load_legislation(FIXTURE_PATH)

    chunks = create_chunks(
        sections,
        max_words=10,
        overlap_words=2,
    )

    assert len(chunks) > 3


def test_split_chunks_have_stable_ids():
    sections = load_legislation(FIXTURE_PATH)

    chunks = create_chunks(
        sections,
        max_words=10,
        overlap_words=2,
    )

    section_one_chunks = [
        chunk
        for chunk in chunks
        if chunk.section_number == "1"
    ]

    assert section_one_chunks[0].chunk_id.endswith(":chunk-1")


def test_invalid_chunk_configuration():
    sections = load_legislation(FIXTURE_PATH)

    with pytest.raises(ValueError):
        create_chunks(sections, max_words=0)

    with pytest.raises(ValueError):
        create_chunks(sections, max_words=10, overlap_words=10)
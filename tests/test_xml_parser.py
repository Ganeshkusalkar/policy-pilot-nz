from pathlib import Path

from src.ingestion.loader import load_legislation


FIXTURE_PATH = Path("data/fixtures/sample_act.xml")


def test_load_legislation():
    sections = load_legislation(FIXTURE_PATH)

    assert len(sections) == 3


def test_first_section():
    sections = load_legislation(FIXTURE_PATH)

    first = sections[0]

    assert first.work_id == "sample_act_1990_001"
    assert first.section_number == "1"
    assert first.heading == "Purpose"
    assert (
        first.text
        == "The purpose of this Act is to provide a clear framework "
        "for the administration of public services."
    )


def test_all_sections_have_required_metadata():
    sections = load_legislation(FIXTURE_PATH)

    for section in sections:
        assert section.work_id
        assert section.title
        assert section.section_number
        assert section.heading
        assert section.text
        assert section.source_url 
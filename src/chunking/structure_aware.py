from dataclasses import dataclass

from src.ingestion.models import LegislationSection


@dataclass
class LegislationChunk:
    chunk_id: str
    work_id: str
    title: str
    part_number: str
    part_title: str
    section_number: str
    section_heading: str
    text: str
    source_url: str


def _split_text(
    text: str,
    max_words: int,
    overlap_words: int,
) -> list[str]:
    words = text.split()

    if len(words) <= max_words:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))

        chunks.append(" ".join(words[start:end]))

        if end == len(words):
            break

        start = end - overlap_words

    return chunks


def create_chunks(
    sections: list[LegislationSection],
    max_words: int = 200,
    overlap_words: int = 40,
) -> list[LegislationChunk]:
    if max_words <= 0:
        raise ValueError("max_words must be greater than zero")

    if overlap_words < 0:
        raise ValueError("overlap_words cannot be negative")

    if overlap_words >= max_words:
        raise ValueError("overlap_words must be smaller than max_words")

    chunks: list[LegislationChunk] = []

    for section in sections:
        text_chunks = _split_text(
            section.text,
            max_words=max_words,
            overlap_words=overlap_words,
        )

        for index, text in enumerate(text_chunks, start=1):
            chunk_id = (
                f"{section.work_id}"
                f":part-{section.part_number}"
                f":section-{section.section_number}"
                f":chunk-{index}"
            )

            chunks.append(
                LegislationChunk(
                    chunk_id=chunk_id,
                    work_id=section.work_id,
                    title=section.title,
                    part_number=section.part_number,
                    part_title=section.part_title,
                    section_number=section.section_number,
                    section_heading=section.heading,
                    text=text,
                    source_url=section.source_url,
                )
            )

    return chunks
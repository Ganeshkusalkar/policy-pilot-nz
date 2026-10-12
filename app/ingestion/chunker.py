
import re


def build_section_url(
    source_url: str,
    provision_id: str,
) -> str:
    """Build a version-specific URL for an official legislation provision."""
    if not source_url or not provision_id:
        return source_url

    base_url = source_url.removesuffix(".xml").rstrip("/")
    return f"{base_url}/sections/{provision_id}/"


def split_text(text: str, max_chars: int = 1200) -> list[str]:
    if max_chars < 100:
        raise ValueError("max_chars must be at least 100.")

    text = re.sub(r"\s+", " ", text).strip()
    chunks = []

    while len(text) > max_chars:
        boundary = max(
            text.rfind(". ", 0, max_chars),
            text.rfind("; ", 0, max_chars),
            text.rfind(" ", 0, max_chars),
        )

        if boundary < max_chars // 2:
            boundary = max_chars

        chunks.append(text[:boundary].strip())
        text = text[boundary:].strip()

    if text:
        chunks.append(text)

    return chunks


def make_chunks(
    provisions: list[dict],
    source_metadata: dict,
    max_chars: int = 1200,
) -> list[dict]:
    chunks = []

    for provision in provisions:
        pieces = split_text(provision["text"], max_chars=max_chars)

        for index, piece in enumerate(pieces):
            label = provision["label"]
            heading = provision["heading"]
            provision_id = provision.get("provision_id") or ""

            context = " ".join(
                value for value in (label, heading) if value
            )

            source_url = source_metadata["source_url"]
            section_url = build_section_url(
                source_url,
                provision_id,
            )

            chunks.append(
                {
                    "chunk_id": (
                        f"{source_metadata['work_id']}:"
                        f"{provision_id or label or 'provision'}:"
                        f"{index + 1}"
                    ),
                    "text": piece,
                    "search_text": f"{context}\n{piece}".strip(),
                    "provision_type": provision["provision_type"],
                    "provision_id": provision_id,
                    "label": label,
                    "heading": heading,
                    "chunk_index": index,
                    "source_title": source_metadata["title"],
                    "work_id": source_metadata["work_id"],
                    "version_id": source_metadata.get("version_id"),
                    "source_url": source_url,
                    "section_url": section_url,
                }
            )

    return chunks


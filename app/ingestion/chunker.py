
import re


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

            context = " ".join(
                value for value in (label, heading) if value
            )

            chunks.append(
                {
                    "chunk_id": (
                        f"{source_metadata['work_id']}:"
                        f"{provision['provision_id'] or label or 'provision'}:"
                        f"{index + 1}"
                    ),
                    "text": piece,
                    "search_text": f"{context}\n{piece}".strip(),
                    "provision_type": provision["provision_type"],
                    "provision_id": provision["provision_id"],
                    "label": label,
                    "heading": heading,
                    "chunk_index": index,
                    "source_title": source_metadata["title"],
                    "work_id": source_metadata["work_id"],
                    "version_id": source_metadata.get("version_id"),
                    "source_url": source_metadata["source_url"],
                }
            )

    return chunks


import json
from pathlib import Path

from app.ingestion.chunker import make_chunks
from app.ingestion.xml_parser import parse_legislation


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "data" / "processed"

BASENAME = "new-zealand-bill-of-rights-act-1990"


def main() -> None:
    xml_path = RAW_DIR / f"{BASENAME}.xml"
    metadata_path = RAW_DIR / f"{BASENAME}.metadata.json"
    output_path = OUTPUT_DIR / f"{BASENAME}.jsonl"

    if not xml_path.exists() or not metadata_path.exists():
        raise FileNotFoundError(
            "Run the official API fetch script first."
        )

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    provisions = parse_legislation(xml_path)
    chunks = make_chunks(provisions, metadata)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"Provisions extracted: {len(provisions)}")
    print(f"Searchable chunks created: {len(chunks)}")
    print(f"Output: {output_path}")

    for chunk in chunks[:3]:
        print(
            f"\n[{chunk['provision_type']} {chunk['label']}] "
            f"{chunk['heading']}"
        )
        print(chunk["text"][:220])


if __name__ == "__main__":
    main()

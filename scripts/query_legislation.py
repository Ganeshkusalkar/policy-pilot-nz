
import json
from pathlib import Path

from app.retrieval.bm25 import BM25Index


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = (
    ROOT
    / "data"
    / "processed"
    / "new-zealand-bill-of-rights-act-1990.jsonl"
)


def load_documents() -> list[dict]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Processed legislation not found. "
            "Run: python -m scripts.process_legislation"
        )

    with DATA_PATH.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def main() -> None:
    documents = load_documents()
    index = BM25Index(documents)

    print(f"Indexed {len(documents)} legislation chunks.")
    print("Ask a question, or type 'exit' to quit.")

    while True:
        query = input("\nQuestion: ").strip()

        if query.lower() in {"exit", "quit"}:
            break

        if not query:
            continue

        results = index.search(query, top_k=3)

        if not results:
            print("No matching provisions found.")
            continue

        for rank, result in enumerate(results, start=1):
            label = result.get("label") or "Unlabelled provision"
            heading = result.get("heading") or "No heading"

            print(f"\n[{rank}] Section {label}: {heading}")
            print(f"BM25 score: {result['score']:.4f}")
            print(result["text"])
            print(
                "Source: "
                f"{result['source_url']} "
                f"(version: {result.get('version_id', 'unknown')})"
            )


if __name__ == "__main__":
    main()

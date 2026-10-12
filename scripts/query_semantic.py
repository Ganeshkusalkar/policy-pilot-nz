
import json
from pathlib import Path

from app.retrieval.semantic import SemanticIndex


DATA_PATH = Path(
    "data/processed/new-zealand-bill-of-rights-act-1990.jsonl"
)


def load_documents() -> list[dict]:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return [
            json.loads(line)
            for line in file
            if line.strip()
        ]


def main() -> None:
    documents = load_documents()
    print(f"Loaded {len(documents)} legislation chunks.")

    print("Loading embedding model and building index...")
    index = SemanticIndex(documents)
    print("Semantic search ready. Type 'exit' to quit.")

    while True:
        query = input("\nQuestion: ").strip()

        if query.lower() in {"exit", "quit"}:
            break

        if not query:
            continue

        for rank, result in enumerate(index.search(query, top_k=3), 1):
            print(
                f"\n{rank}. Section {result.get('label')} | "
                f"{result.get('heading')}"
            )
            print(f"Similarity: {result['score']:.4f}")
            print(result.get("text", ""))
            print(f"Source: {result.get('source_url', '')}")


if __name__ == "__main__":
    main()


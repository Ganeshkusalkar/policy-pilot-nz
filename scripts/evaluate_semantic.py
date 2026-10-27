
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.semantic import SemanticIndex

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "new-zealand-bill-of-rights-act-1990.jsonl"
)
QUESTIONS_PATH = PROJECT_ROOT / "data" / "evaluation" / "retrieval_questions.json"
TOP_K = 3


def load_jsonl(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_questions(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def expected_labels(item: dict) -> set[str]:
    values = (
        item.get("expected_sections")
        or item.get("expected_labels")
        or item.get("expected_section")
        or item.get("expected_label")
    )
    if values is None:
        raise ValueError(f"Missing expected section in: {item}")

    if not isinstance(values, list):
        values = [values]

    return {str(value).strip() for value in values}


def main() -> None:
    documents = load_jsonl(DATA_PATH)
    questions = load_questions(QUESTIONS_PATH)

    print(f"Documents: {len(documents)}")
    print(f"Evaluation questions: {len(questions)}")
    print("Building semantic index...")

    index = SemanticIndex(documents)

    hits_at_k = 0
    reciprocal_rank_sum = 0.0
    query_times = []

    for item in questions:
        question = item.get("question") or item.get("query")
        if not question:
            raise ValueError(f"Missing question text: {item}")

        expected = expected_labels(item)

        start = time.perf_counter()
        results = index.search(question, top_k=TOP_K)
        query_times.append(time.perf_counter() - start)

        ranks = [
            rank
            for rank, result in enumerate(results, start=1)
            if str(result.get("label", "")).strip() in expected
        ]

        if ranks:
            hits_at_k += 1
            reciprocal_rank_sum += 1.0 / min(ranks)

        best_rank = min(ranks) if ranks else None
        print(
            f"{'PASS' if best_rank == 1 else 'MISS' if not ranks else 'PARTIAL'}"
            f" | rank={best_rank or '-'}"
            f" | expected={sorted(expected)}"
            f" | {question}"
        )

    total = len(questions)
    if total == 0:
        raise ValueError("Evaluation dataset is empty.")


    print("\nSemantic Retrieval Evaluation")
    print("=" * 40)
    print(f"Questions: {total}")
    print(f"Recall@{TOP_K}: {hits_at_k / total:.3f}")
    print(f"MRR: {reciprocal_rank_sum / total:.3f}")
    print(
        "Average query time: "
        f"{sum(query_times) / len(query_times) * 1000:.2f} ms"
    )


if __name__ == "__main__":
    main()



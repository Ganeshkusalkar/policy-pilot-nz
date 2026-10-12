
import json
import time
from pathlib import Path

from app.retrieval.hybrid import HybridIndex

DATA_PATH = Path(
    "data/processed/new-zealand-bill-of-rights-act-1990.jsonl"
)
QUESTIONS_PATH = Path("data/evaluation/retrieval_questions.json")
TOP_K = 3


def load_jsonl(path):
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_questions(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def expected_labels(item):
    values = (
        item.get("expected_sections")
        or item.get("expected_labels")
        or item.get("expected_section")
        or item.get("expected_label")
    )
    if values is None:
        raise ValueError(f"Missing expected section: {item}")

    if not isinstance(values, list):
        values = [values]

    return {str(value).strip() for value in values}


def main():
    documents = load_jsonl(DATA_PATH)
    questions = load_questions(QUESTIONS_PATH)

    print(f"Documents: {len(documents)}")
    print(f"Evaluation questions: {len(questions)}")
    print("Building hybrid index...")

    index = HybridIndex(documents)

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

        best_rank = min(ranks) if ranks else None

        if best_rank is not None:
            hits_at_k += 1
            reciprocal_rank_sum += 1.0 / best_rank

        status = (
            "PASS" if best_rank == 1
            else "PARTIAL" if best_rank is not None
            else "MISS"
        )

        print(
            f"{status} | rank={best_rank or '-'} "
            f"| expected={sorted(expected)} | {question}"
        )

    total = len(questions)
    if total == 0:
        raise ValueError("No evaluation questions found.")

    print("\nHybrid Retrieval Evaluation")
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

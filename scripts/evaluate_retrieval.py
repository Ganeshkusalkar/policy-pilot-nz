
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.bm25 import BM25Index

DOCUMENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "new-zealand-bill-of-rights-act-1990.jsonl"
)

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "retrieval_questions.json"
)

TOP_K = 3


def load_documents():
    with DOCUMENTS_PATH.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_questions():
    with QUESTIONS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    documents = load_documents()
    questions = load_questions()
    index = BM25Index(documents)

    reciprocal_ranks = []
    successful_retrievals = 0

    print("\nPolicyPilot NZ — BM25 Retrieval Evaluation")
    print("=" * 48)

    for item in questions:
        question = item["question"]
        expected_labels = set(item["expected_labels"])

        results = index.search(question, top_k=TOP_K)

        relevant_rank = next(
            (
                rank
                for rank, result in enumerate(results, start=1)
                if str(result.get("label", "")).strip()
                in expected_labels
            ),
            None,
        )

        if relevant_rank is not None:
            successful_retrievals += 1
            reciprocal_ranks.append(1 / relevant_rank)
        else:
            reciprocal_ranks.append(0.0)

        print(f"\nQuestion: {question}")
        print(f"Expected section(s): {sorted(expected_labels)}")

        if relevant_rank is None:
            print(f"Correct section not found in top {TOP_K}.")
        else:
            print(f"Correct section found at rank {relevant_rank}.")

        for rank, result in enumerate(results, start=1):
            print(
                f"  {rank}. Section {result.get('label', '?')} "
                f"| score={result.get('score', 0):.4f}"
            )
            print(f"     {result.get('heading', '')}")

    total = len(questions)

    recall_at_k = successful_retrievals / total if total else 0.0
    mrr = sum(reciprocal_ranks) / total if total else 0.0

    print("\n" + "=" * 48)
    print(f"Questions evaluated: {total}")
    print(f"Recall@{TOP_K}: {recall_at_k:.3f}")
    print(f"MRR:          {mrr:.3f}")


if __name__ == "__main__":
    main()

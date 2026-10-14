
from typing import Any

from app.retrieval.bm25 import BM25Index
from app.retrieval.semantic import SemanticIndex


class HybridIndex:
    """Combine keyword and semantic rankings with Reciprocal Rank Fusion."""

    def __init__(
        self,
        documents: list[dict[str, Any]],
        model_name: str | None = None,
        rank_constant: int = 60,
    ) -> None:
        if not documents:
            raise ValueError("Cannot build a hybrid index without documents.")
        if rank_constant < 1:
            raise ValueError("rank_constant must be at least 1.")

        self.documents = documents
        self.rank_constant = rank_constant
        self.bm25 = BM25Index(documents)

        if model_name is None:
            self.semantic = SemanticIndex(documents)
        else:
            self.semantic = SemanticIndex(documents, model_name=model_name)

    @staticmethod
    def _document_key(document: dict[str, Any]) -> str:
        return str(
            document.get("chunk_id")
            or document.get("provision_id")
            or document.get("label")
        )

    def search(
        self, query: str, top_k: int = 3
    ) -> list[dict[str, Any]]:
        if not query.strip():
            return []
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        # Retrieve complete rankings so fusion can consider every document.
        bm25_results = self.bm25.search(query, top_k=len(self.documents))
        semantic_results = self.semantic.search(
            query, top_k=len(self.documents)
        )

        fused: dict[str, dict[str, Any]] = {}

        for results, source in (
            (bm25_results, "bm25"),
            (semantic_results, "semantic"),
        ):
            for rank, document in enumerate(results, start=1):
                key = self._document_key(document)

                if key not in fused:
                    fused[key] = {
                        "document": dict(document),
                        "rrf_score": 0.0,
                    }

                fused[key]["rrf_score"] += 1.0 / (
                    self.rank_constant + rank
                )
                fused[key][f"{source}_rank"] = rank
                fused[key][f"{source}_score"] = document.get("score")

        ranked = sorted(
            fused.values(),
            key=lambda item: item["rrf_score"],
            reverse=True,
        )

        output = []
        for item in ranked[:top_k]:
            result = item["document"]
            result["score"] = item["rrf_score"]
            result["rrf_score"] = item["rrf_score"]
            result["bm25_rank"] = item.get("bm25_rank")
            result["semantic_rank"] = item.get("semantic_rank")
            result["bm25_score"] = item.get("bm25_score")
            result["semantic_score"] = item.get("semantic_score")
            output.append(result)

        return output

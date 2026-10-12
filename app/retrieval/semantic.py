
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer


DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class SemanticIndex:
    """Retrieve legislation using embedding similarity."""

    def __init__(
        self,
        documents: list[dict[str, Any]],
        model_name: str = DEFAULT_MODEL,
    ) -> None:
        if not documents:
            raise ValueError("Cannot build a semantic index without documents.")

        self.documents = documents
        self.model = SentenceTransformer(model_name)

        # Include section labels and headings when available.
        self.texts = [
            str(doc.get("search_text") or doc.get("text") or "")
            for doc in documents
        ]

        self.embeddings = self.model.encode(
            self.texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """Return the top matching documents and similarity scores."""
        if not query.strip():
            return []

        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]

        # Normalized embeddings make dot product equal cosine similarity.
        scores = self.embeddings @ query_embedding
        ranked_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for index in ranked_indices:
            result = dict(self.documents[int(index)])
            result["score"] = float(scores[index])
            results.append(result)

        return results


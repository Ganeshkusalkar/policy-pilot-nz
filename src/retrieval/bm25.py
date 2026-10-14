import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from src.chunking.structure_aware import LegislationChunk


@dataclass
class RetrievalResult:
    chunk: LegislationChunk
    score: float


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


class BM25Retriever:
    def __init__(self, chunks: list[LegislationChunk]):
        if not chunks:
            raise ValueError("At least one chunk is required")

        self.chunks = chunks
        self.tokenized_chunks = [
            _tokenize(chunk.text)
            for chunk in chunks
        ]

        self.index = BM25Okapi(self.tokenized_chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        if not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        scores = self.index.get_scores(_tokenize(query))

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:top_k]

        return [
            RetrievalResult(
                chunk=self.chunks[index],
                score=float(scores[index]),
            )
            for index in ranked_indices
        ]
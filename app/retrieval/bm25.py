
import math
import re
from collections import Counter



STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "does", "for", "from", "how", "in", "is", "it",
    "of", "on", "or", "the", "this", "to", "was",
    "what", "which", "who", "with",
}


LEGAL_SYNONYMS = {
    "invalidate": ["invalid", "ineffective"],
    "invalid": ["invalidate", "ineffective"],
    "conflict": ["inconsistent"],
    "conflicts": ["inconsistent"],
    "conflicting": ["inconsistent"],
    "inconsistent": ["conflict"],
    "inconsistency": ["inconsistent"],
    "enactment": ["provision", "legislation"],
    "enactments": ["provisions", "legislation"],
}



def normalize_token(token: str) -> str:
    """Apply conservative normalization for common word variants."""
    token = token.lower()

    # Handle irregular and common legal word forms.
    special_forms = {
        "arbitrarily": "arbitrary",
        "arbitrary": "arbitrary",
        "detained": "detain",
        "detaining": "detain",
        "detention": "detain",
        "detentions": "detain",
        "arrested": "arrest",
        "arrests": "arrest",
        "arresting": "arrest",
        "enactments": "enactment",
        "provisions": "provision",
    }

    if token in special_forms:
        return special_forms[token]

    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"

    if len(token) > 5 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]

    if len(token) > 6 and token.endswith("ed"):
        token = token[:-2]

    if len(token) > 5 and token.endswith("es"):
        token = token[:-2]

    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        token = token[:-1]

    return token



def tokenize(text: str) -> list[str]:
    """Normalize words and remove common words that add little relevance."""
    raw_tokens = re.findall(r"[a-z0-9]+", text.lower())

    return [
        normalized
        for token in raw_tokens
        if token not in STOPWORDS
        for normalized in [normalize_token(token)]
        if normalized and normalized not in STOPWORDS
    ]



class BM25Index:
    """Small dependency-free BM25 index for legislation chunks."""

    def __init__(
        self,
        documents: list[dict],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        if not documents:
            raise ValueError("Cannot index an empty document collection.")

        self.documents = documents
        self.k1 = k1
        self.b = b
        self.tokenized = [
            tokenize(doc.get("search_text") or doc.get("text", ""))
            for doc in documents
        ]
        self.lengths = [len(tokens) for tokens in self.tokenized]
        self.avg_length = sum(self.lengths) / len(self.lengths) or 1.0

        self.term_frequencies = [Counter(tokens) for tokens in self.tokenized]
        self.document_frequency = Counter()

        for frequencies in self.term_frequencies:
            self.document_frequency.update(frequencies.keys())

        count = len(documents)
        self.idf = {
            term: math.log(
                1 + (count - frequency + 0.5) / (frequency + 0.5)
            )
            for term, frequency in self.document_frequency.items()
        }

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if top_k < 1:
            raise ValueError("top_k must be at least 1.")

        
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # Add related legal terms to improve vocabulary matching.
        expanded_tokens = list(query_tokens)

        for token in query_tokens:
            expanded_tokens.extend(
                normalize_token(synonym)
                for synonym in LEGAL_SYNONYMS.get(token, [])
            )

        query_tokens = expanded_tokens


        results = []

        for index, document in enumerate(self.documents):
            frequencies = self.term_frequencies[index]
            length = self.lengths[index]
            score = 0.0

            for term in query_tokens:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue

                idf = self.idf.get(term, 0.0)
                denominator = frequency + self.k1 * (
                    1 - self.b + self.b * length / self.avg_length
                )
                score += (
                    idf
                    * frequency
                    * (self.k1 + 1)
                    / denominator
                )

            if score > 0:
                results.append({**document, "score": score})

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]


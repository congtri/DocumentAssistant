"""RAG quality metrics."""


def recall_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    """Fraction of relevant items found in top-k retrieved."""
    if not relevant:
        return 0.0
    retrieved_k = set(retrieved[:k])
    hits = len(set(relevant) & retrieved_k)
    return hits / len(relevant)


def precision_at_k(relevant: list[str], retrieved: list[str], k: int) -> float:
    """Fraction of top-k retrieved items that are relevant."""
    if k == 0:
        return 0.0
    retrieved_k = retrieved[:k]
    hits = len(set(relevant) & set(retrieved_k))
    return hits / k


def mrr(relevant: list[str], retrieved: list[str]) -> float:
    """Mean Reciprocal Rank: 1/rank of the first relevant item."""
    for i, item in enumerate(retrieved):
        if item in relevant:
            return 1.0 / (i + 1)
    return 0.0


def hit_rate(relevant: list[str], retrieved: list[str], k: int) -> float:
    """Whether at least one relevant item appears in top-k. Returns 0 or 1."""
    retrieved_k = set(retrieved[:k])
    return 1.0 if set(relevant) & retrieved_k else 0.0

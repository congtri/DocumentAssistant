"""Benchmark runner for RAG evaluation."""

from dataclasses import dataclass

from backend.core.logger import logger
from backend.evaluation.metrics import recall_at_k, precision_at_k, mrr, hit_rate


@dataclass
class BenchmarkCase:
    """A single evaluation case."""

    query: str
    relevant_ids: list[str]


@dataclass
class BenchmarkResult:
    """Aggregated benchmark results."""

    recall: float
    precision: float
    mrr: float
    hit_rate: float
    num_cases: int


class BenchmarkRunner:
    """Runs evaluation benchmarks against a retriever."""

    def __init__(self, retriever):
        self._retriever = retriever

    def run(self, cases: list[BenchmarkCase], k: int = 5) -> BenchmarkResult:
        """Execute benchmark cases and compute aggregate metrics."""
        recalls = []
        precisions = []
        mrrs = []
        hits = []

        for case in cases:
            results = self._retriever.search(case.query, top_k=k)
            retrieved_ids = [chunk.chunk_id for chunk, _ in results]

            recalls.append(recall_at_k(case.relevant_ids, retrieved_ids, k))
            precisions.append(precision_at_k(case.relevant_ids, retrieved_ids, k))
            mrrs.append(mrr(case.relevant_ids, retrieved_ids))
            hits.append(hit_rate(case.relevant_ids, retrieved_ids, k))

        n = len(cases) or 1
        result = BenchmarkResult(
            recall=sum(recalls) / n,
            precision=sum(precisions) / n,
            mrr=sum(mrrs) / n,
            hit_rate=sum(hits) / n,
            num_cases=len(cases),
        )
        logger.info(
            f"Benchmark: Recall@{k}={result.recall:.3f} "
            f"Precision@{k}={result.precision:.3f} "
            f"MRR={result.mrr:.3f} HitRate={result.hit_rate:.3f}"
        )
        return result

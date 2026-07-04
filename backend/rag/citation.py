from backend.domain.models import Citation, Chunk


def format_citations(citations: list[Citation]) -> str:
    if not citations:
        return ""

    lines = ["\n\nSources:"]
    seen = set()

    for citation in citations:
        key = f"{citation.source}:{citation.page}"
        if key in seen:
            continue
        seen.add(key)

        entry = f"  - {citation.source}"
        if citation.page:
            entry += f" (page {citation.page})"
        if citation.heading:
            entry += f" [{citation.heading}]"
        lines.append(entry)

    return "\n".join(lines)


def extract_citations(chunks_with_scores: list[tuple]) -> list[Citation]:
    citations = []
    for chunk, score in chunks_with_scores:
        citations.append(Citation(
            source=chunk.source,
            page=chunk.page,
            heading=chunk.heading,
            relevance_score=score,
        ))
    return citations

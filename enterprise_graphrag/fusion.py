from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Hit:
    doc_id: str
    title: str
    tenant_id: str
    text: str
    score: float
    source: str
    metadata: dict


def weighted_rrf(
    lists: dict[str, list[Hit]],
    weights: dict[str, float],
    k: int = 60,
    limit: int = 8,
) -> list[Hit]:
    merged = {}

    for source, hits in lists.items():
        weight = float(weights.get(source, 1.0))
        for rank, hit in enumerate(hits, start=1):
            contribution = weight / (k + rank)
            current = merged.get(hit.doc_id)
            if current is None:
                merged[hit.doc_id] = (hit, contribution, {source})
            else:
                previous, previous_score, sources = current
                merged[hit.doc_id] = (
                    previous,
                    previous_score + contribution,
                    sources | {source},
                )

    ranked = sorted(
        merged.values(),
        key=lambda item: (-item[1], item[0].doc_id),
    )

    return [
        Hit(
            doc_id=hit.doc_id,
            title=hit.title,
            tenant_id=hit.tenant_id,
            text=hit.text,
            score=float(score),
            source="+".join(sorted(sources)),
            metadata={
                **hit.metadata,
                "rrf_sources": sorted(sources),
            },
        )
        for hit, score, sources in ranked[:limit]
    ]

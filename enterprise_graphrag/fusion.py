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


def weighted_rrf(lists: dict[str, list[Hit]], weights: dict[str, float], k: int = 60, limit: int = 8) -> list[Hit]:
    merged: dict[str, tuple[Hit, float, set[str]]] = {}
    for source, hits in lists.items():
        for rank, hit in enumerate(hits, 1):
            old = merged.get(hit.doc_id)
            score = weights.get(source, 1.0) / (k + rank)
            if old:
                merged[hit.doc_id] = (old[0], old[1] + score, old[2] | {source})
            else:
                merged[hit.doc_id] = (hit, score, {source})
    result = []
    for hit, score, sources in sorted(merged.values(), key=lambda x: x[1], reverse=True)[:limit]:
        result.append(Hit(hit.doc_id, hit.title, hit.tenant_id, hit.text, score, "+".join(sorted(sources))))
    return result

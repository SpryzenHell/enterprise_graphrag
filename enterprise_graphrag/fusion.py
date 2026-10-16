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
    if k < 1:
        raise ValueError("RRF k must be greater than zero")
    if limit < 1:
        raise ValueError("RRF limit must be greater than zero")

    merged = {}

    for source, hits in lists.items():
        weight = float(weights.get(source, 1.0))
        if weight < 0:
            raise ValueError("RRF weights cannot be negative")
        for rank, hit in enumerate(hits, start=1):
            contribution = weight / (k + rank)
            key = (hit.tenant_id, hit.doc_id)
            current = merged.get(key)
            if current is None:
                merged[key] = (hit, contribution, {source})
            else:
                previous, previous_score, sources = current
                merged[key] = (
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


def prefix_protected_rrf(
    vector_hits: list[Hit],
    graph_hits: list[Hit],
    weights: dict[str, float],
    k: int = 60,
    limit: int = 8,
    candidate_limit: int | None = None,
    protected_prefix: int = 0,
) -> list[Hit]:
    """Fuse retrieval while optionally keeping a head of the vector ranking fixed.

    The protected vector prefix is retained in its original order. Weighted RRF
    orders the tail. The function can return more candidates than the final answer
    limit so the security gateway can remove blocked passages and still refill the
    result. Set protected_prefix=0 for ordinary weighted RRF.
    """
    if limit < 1:
        raise ValueError("limit must be greater than zero")
    fetch_limit = limit if candidate_limit is None else candidate_limit
    if fetch_limit < limit:
        raise ValueError("candidate_limit must be greater than or equal to limit")
    if protected_prefix < 0:
        raise ValueError("protected_prefix cannot be negative")

    prefix_count = min(protected_prefix, limit, len(vector_hits))
    original_prefix = vector_hits[:prefix_count]
    prefix = [
        Hit(
            doc_id=hit.doc_id,
            title=hit.title,
            tenant_id=hit.tenant_id,
            text=hit.text,
            score=hit.score,
            source="vector_protected_prefix",
            metadata={
                **hit.metadata,
                "rrf_sources": ["vector"],
                "vector_prefix_protected": True,
            },
        )
        for hit in original_prefix
    ]
    prefix_keys = {(hit.tenant_id, hit.doc_id) for hit in original_prefix}

    ranked_tail = weighted_rrf(
        {"vector": vector_hits, "graph": graph_hits},
        weights,
        k=k,
        limit=fetch_limit,
    )
    tail = [
        hit for hit in ranked_tail
        if (hit.tenant_id, hit.doc_id) not in prefix_keys
    ]
    seen = prefix_keys | {(hit.tenant_id, hit.doc_id) for hit in tail}

    # If fusion produced fewer unique candidates than requested, refill from
    # vector ranking order. This does not promote a graph-only result over the
    # vector prefix, and preserves a full security-screening pool where possible.
    for hit in vector_hits:
        key = (hit.tenant_id, hit.doc_id)
        if key in seen:
            continue
        tail.append(hit)
        seen.add(key)
        if len(tail) >= fetch_limit - len(prefix):
            break

    return (prefix + tail[: max(0, fetch_limit - len(prefix))])[:fetch_limit]

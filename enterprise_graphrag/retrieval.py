from __future__ import annotations

import re
from collections import defaultdict

from .fusion import Hit, weighted_rrf
from .security import SecurityGateway


class TenantMemoryGraph:
    """Small CI/demo graph mirroring the Neo4j tenant boundary."""

    ENTITY_PATTERN = re.compile(
        r"\b[A-Z][A-Za-z0-9&.-]{2,}\b"
    )

    def __init__(self) -> None:
        self.docs = defaultdict(dict)
        self.entities = defaultdict(
            lambda: defaultdict(set)
        )

    def add(
        self,
        tenant: str,
        doc: dict,
    ) -> None:
        doc_id = doc["doc_id"]

        # Upserts must remove stale entity memberships before indexing the
        # replacement text; otherwise the graph can keep returning a document
        # for entities that no longer occur in the current document.
        previous = self.docs[tenant].get(doc_id)
        if previous:
            for entity in self.ENTITY_PATTERN.findall(
                previous["text"]
            ):
                key = entity.lower()
                doc_ids = self.entities[tenant].get(key)
                if doc_ids is None:
                    continue
                doc_ids.discard(doc_id)
                if not doc_ids:
                    self.entities[tenant].pop(
                        key,
                        None,
                    )

        self.docs[tenant][doc_id] = dict(doc)

        for entity in self.ENTITY_PATTERN.findall(
            doc["text"]
        ):
            self.entities[tenant][
                entity.lower()
            ].add(doc_id)

    def search(
        self,
        tenant: str,
        query: str,
        limit: int,
    ) -> list[Hit]:
        terms = {
            token.lower()
            for token in re.findall(
                r"[A-Za-z0-9]{3,}",
                query,
            )
        }
        scores = defaultdict(float)

        for entity, docs in self.entities[tenant].items():
            if any(
                term in entity
                for term in terms
            ):
                for doc_id in docs:
                    scores[doc_id] += 2.0

        for doc_id, doc in self.docs[tenant].items():
            haystack = (
                doc["title"] + " " + doc["text"]
            ).lower()
            scores[doc_id] += 0.25 * sum(
                term in haystack
                for term in terms
            )

        ranked = sorted(
            scores.items(),
            key=lambda pair: (-pair[1], pair[0]),
        )[:limit]

        return [
            Hit(
                doc_id=doc_id,
                title=self.docs[tenant][doc_id]["title"],
                tenant_id=tenant,
                text=self.docs[tenant][doc_id]["text"],
                score=float(score),
                source="graph",
                metadata=self.docs[tenant][doc_id],
            )
            for doc_id, score in ranked
        ]

    def trace(
        self,
        tenant: str,
        doc_ids: list[str],
    ) -> dict:
        nodes = {}
        edges = set()

        for doc_id in doc_ids:
            doc = self.docs[tenant].get(doc_id)
            if not doc:
                continue

            nodes[doc_id] = {
                "id": doc_id,
                "label": doc["title"],
                "type": "document",
                "tenant_id": tenant,
            }

            for entity in self.ENTITY_PATTERN.findall(
                doc["text"]
            )[:8]:
                entity_id = (
                    f"entity:{tenant}:{entity.lower()}"
                )
                nodes[entity_id] = {
                    "id": entity_id,
                    "label": entity,
                    "type": "entity",
                    "tenant_id": tenant,
                }
                edges.add(
                    (doc_id, entity_id, "MENTIONS")
                )

        return {
            "nodes": list(nodes.values()),
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "type": kind,
                }
                for source, target, kind in sorted(edges)
            ],
        }


class HybridRetriever:
    def __init__(
        self,
        vector,
        graph,
        security: SecurityGateway,
        vector_weight: float,
        graph_weight: float,
        rrf_k: int,
    ) -> None:
        self.vector = vector
        self.graph = graph
        self.security = security
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight
        self.rrf_k = rrf_k

    def add(
        self,
        tenant: str,
        documents: list[dict],
    ) -> None:
        for document in documents:
            self.graph.add(
                tenant,
                document,
            )
        self.vector.add(
            tenant,
            documents,
        )

    def search(
        self,
        tenant: str,
        query: str,
        limit: int,
    ):
        vector_hits = self.vector.search(
            tenant,
            query,
            limit,
        )
        graph_hits = self.graph.search(
            tenant,
            query,
            limit,
        )

        fused = weighted_rrf(
            {
                "vector": vector_hits,
                "graph": graph_hits,
            },
            {
                "vector": self.vector_weight,
                "graph": self.graph_weight,
            },
            k=self.rrf_k,
            limit=limit,
        )

        allowed = []
        blocked = []

        for hit in fused:
            if hit.tenant_id != tenant:
                blocked.append(
                    {
                        "doc_id": hit.doc_id,
                        "reason": "tenant mismatch",
                    }
                )
                continue

            decision = self.security.inspect(
                hit.text,
                direct=False,
            )
            if decision["allowed"]:
                allowed.append(hit)
            else:
                blocked.append(
                    {
                        "doc_id": hit.doc_id,
                        "reason": decision["reason"],
                        "marker_count": decision["marker_count"],
                        "perplexity": decision["perplexity"],
                    }
                )

        return (
            allowed,
            blocked,
            len(vector_hits),
            len(graph_hits),
        )

    def trace(
        self,
        tenant: str,
        doc_ids: list[str],
    ):
        if hasattr(
            self.graph,
            "trace",
        ):
            return self.graph.trace(
                tenant,
                doc_ids,
            )
        return {
            "nodes": [],
            "edges": [],
        }

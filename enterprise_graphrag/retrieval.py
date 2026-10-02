from __future__ import annotations

import re
from collections import defaultdict

from .fusion import Hit, weighted_rrf
from .security import SecurityGateway


class TenantMemoryGraph:
    def __init__(self):
        self.docs = defaultdict(dict)
        self.entities = defaultdict(lambda: defaultdict(set))

    def add(self, tenant: str, doc: dict):
        self.docs[tenant][doc["doc_id"]] = doc
        for entity in re.findall(r"\b[A-Z][A-Za-z0-9&.-]{2,}\b", doc["text"]):
            self.entities[tenant][entity.lower()].add(doc["doc_id"])

    def search(self, tenant: str, query: str, limit: int):
        terms = {x.lower() for x in re.findall(r"[A-Za-z0-9]{3,}", query)}
        scores = defaultdict(float)
        for entity, docs in self.entities[tenant].items():
            if any(term in entity for term in terms):
                for doc_id in docs:
                    scores[doc_id] += 2.0
        for doc_id, doc in self.docs[tenant].items():
            text = (doc["title"] + " " + doc["text"]).lower()
            scores[doc_id] += 0.25 * sum(term in text for term in terms)
        return [Hit(d, self.docs[tenant][d]["title"], tenant, self.docs[tenant][d]["text"], s, "graph") for d, s in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]]


class HybridRetriever:
    def __init__(self, graph: TenantMemoryGraph, security: SecurityGateway):
        self.graph = graph
        self.security = security
        self.vector_docs = defaultdict(dict)

    def add(self, tenant: str, documents: list[dict]):
        for doc in documents:
            self.graph.add(tenant, doc)
            self.vector_docs[tenant][doc["doc_id"]] = doc

    def vector_search(self, tenant: str, query: str, limit: int):
        terms = {x.lower() for x in re.findall(r"[A-Za-z0-9]{3,}", query)}
        scored = []
        for doc in self.vector_docs[tenant].values():
            text = (doc["title"] + " " + doc["text"]).lower()
            score = sum(term in text for term in terms)
            if score:
                scored.append(Hit(doc["doc_id"], doc["title"], tenant, doc["text"], float(score), "vector"))
        return sorted(scored, key=lambda x: x.score, reverse=True)[:limit]

    def search(self, tenant: str, query: str, limit: int = 8):
        vector = self.vector_search(tenant, query, limit)
        graph = self.graph.search(tenant, query, limit)
        fused = weighted_rrf({"vector": vector, "graph": graph}, {"vector": 0.55, "graph": 0.45}, limit=limit)
        allowed, blocked = [], []
        for hit in fused:
            decision = self.security.inspect(hit.text)
            if decision["allowed"]:
                allowed.append(hit)
            else:
                blocked.append({"doc_id": hit.doc_id, "reason": decision["reason"]})
        return allowed, blocked, len(vector), len(graph)

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
from collections import defaultdict
from pathlib import Path

from .fusion import Hit, weighted_rrf
from .schemas import validate_documents
from .security import SecurityGateway


class TenantMemoryGraph:
    """Small CI/demo graph mirroring the Neo4j tenant boundary."""

    ENTITY_PATTERN = re.compile(
        r"\b[A-Z][A-Za-z0-9&.-]{2,}\b"
    )

    def __init__(self, persistence_path: str | None = None) -> None:
        self._lock = threading.RLock()
        self.persistence_path = Path(persistence_path) if persistence_path else None
        self.docs = defaultdict(dict)
        self.entities = defaultdict(
            lambda: defaultdict(set)
        )
        self.doc_entities = defaultdict(dict)
        if self.persistence_path is not None:
            self._load_persisted()

    def add(
        self,
        tenant: str,
        doc: dict,
    ) -> None:
        with self._lock:
            self._add_locked(
                tenant,
                doc,
            )
            self._persist()

    def _load_persisted(self) -> None:
        path = self.persistence_path
        if path is None or not path.exists():
            return

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"Invalid persisted memory graph: {path}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError(
                f"Invalid persisted memory graph: {path}"
            )

        for tenant, documents in payload.items():
            if not isinstance(tenant, str) or not isinstance(documents, list):
                raise ValueError(
                    f"Invalid persisted memory graph tenant data: {path}"
                )
            for document in documents:
                if not isinstance(document, dict):
                    raise ValueError(
                        f"Invalid persisted memory graph document: {path}"
                    )
                self._add_locked(tenant, document)

    def _persist(self) -> None:
        path = self.persistence_path
        if path is None:
            return

        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            tenant: list(documents.values())
            for tenant, documents in self.docs.items()
        }
        fd, temp_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temp_name, 0o600)
            os.replace(temp_name, path)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass

    def _add_locked(
        self,
        tenant: str,
        doc: dict,
    ) -> None:
        doc_id = doc["doc_id"]

        # Upserts must remove stale entity memberships before indexing the
        # replacement text; otherwise the graph can keep returning a document
        # for entities that no longer occur in the current document.
        previous_entities = self.doc_entities[tenant].pop(
            doc_id,
            set(),
        )
        for key in previous_entities:
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

        entity_keys = {
            entity.lower()
            for entity in self.ENTITY_PATTERN.findall(
                doc["text"]
            )
        }
        self.doc_entities[tenant][doc_id] = entity_keys
        for key in entity_keys:
            self.entities[tenant][key].add(doc_id)

    def search(
        self,
        tenant: str,
        query: str,
        limit: int,
    ) -> list[Hit]:
        with self._lock:
            return self._search_locked(
                tenant,
                query,
                limit,
            )

    def _search_locked(
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
            lexical_overlap = sum(
                term in haystack
                for term in terms
            )
            if lexical_overlap:
                scores[doc_id] += 0.25 * lexical_overlap

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
        with self._lock:
            return self._trace_locked(
                tenant,
                doc_ids,
            )

    def _trace_locked(
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
        normalized = validate_documents(
            tenant,
            documents,
        )
        if not normalized:
            return

        # Perform external/vector work before mutating the graph fallback.
        # This prevents embedding/provider failures from leaving a graph-only
        # document that was never successfully indexed in the vector backend.
        self.vector.add(
            tenant,
            normalized,
        )
        for document in normalized:
            self.graph.add(
                tenant,
                document,
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
                hit.title + "\n" + hit.text,
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

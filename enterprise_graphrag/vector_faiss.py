from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path

import numpy as np

from .embeddings import Embedder
from .fusion import Hit


class TenantFAISS:
    """One FAISS HNSW index per tenant; tenant isolation is physical."""

    def __init__(
        self,
        root: str,
        embedder: Embedder,
    ) -> None:
        import faiss

        self.faiss = faiss
        self.root = Path(root)
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.indexes: dict[str, object] = {}
        self.meta: dict[str, dict[str, dict]] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _tenant_key(tenant: str) -> str:
        return hashlib.sha256(
            tenant.encode("utf-8")
        ).hexdigest()[:24]

    def _paths(self, tenant: str):
        key = self._tenant_key(tenant)
        return (
            self.root / f"{key}.faiss",
            self.root / f"{key}.json",
        )

    def _new_index(self):
        base = self.faiss.IndexHNSWFlat(
            self.dimension,
            32,
            self.faiss.METRIC_INNER_PRODUCT,
        )
        base.hnsw.efConstruction = 80
        base.hnsw.efSearch = 64
        return self.faiss.IndexIDMap2(base)

    def _load(self, tenant: str):
        with self._lock:
            if tenant in self.indexes:
                return self.indexes[tenant]

            index_path, meta_path = self._paths(tenant)

            if index_path.exists() and meta_path.exists():
                index = self.faiss.read_index(
                    str(index_path)
                )
                self.meta[tenant] = json.loads(
                    meta_path.read_text(
                        encoding="utf-8"
                    )
                )
                if index.d != self.dimension:
                    raise ValueError(
                        f"FAISS dimension mismatch for tenant={tenant}: "
                        f"index={index.d}, embedder={self.dimension}"
                    )
            else:
                index = self._new_index()
                self.meta[tenant] = {}

            self.indexes[tenant] = index
            return index

    def _embed(self, documents: list[dict]) -> np.ndarray:
        matrix = np.asarray(
            self.embedder.embed(
                [
                    doc["title"]
                    + "\n"
                    + doc["text"]
                    for doc in documents
                ]
            ),
            dtype="float32",
        )
        self.faiss.normalize_L2(matrix)
        return matrix

    def _persist(
        self,
        tenant: str,
        index,
        metadata: dict[str, dict],
    ) -> None:
        index_path, meta_path = self._paths(tenant)
        self.faiss.write_index(
            index,
            str(index_path),
        )
        meta_path.write_text(
            json.dumps(
                metadata,
                indent=2,
            ),
            encoding="utf-8",
        )

    def _rebuild(
        self,
        tenant: str,
        documents: list[dict],
    ) -> None:
        index = self._new_index()
        matrix = self._embed(documents)

        if documents:
            ids = np.arange(
                len(documents),
                dtype=np.int64,
            )
            index.add_with_ids(
                matrix,
                ids,
            )
            metadata = {
                str(vector_id): document
                for vector_id, document in zip(
                    ids.tolist(),
                    documents,
                )
            }
        else:
            metadata = {}

        self.indexes[tenant] = index
        self.meta[tenant] = metadata
        self._persist(
            tenant,
            index,
            metadata,
        )

    def add(
        self,
        tenant: str,
        documents: list[dict],
    ) -> None:
        if not documents:
            return

        # Treat doc_id as the tenant-local primary key. This makes ingestion
        # idempotent and prevents a replayed batch from creating duplicates.
        documents_by_id = {
            document["doc_id"]: dict(document)
            for document in documents
        }
        documents = list(documents_by_id.values())
        if not documents:
            return

        with self._lock:
            index = self._load(tenant)
            existing_by_vector_id = self.meta[tenant]
            replacement_ids = {
                document["doc_id"]
                for document in documents
            }
            has_replacements = any(
                existing.get("doc_id") in replacement_ids
                for existing in existing_by_vector_id.values()
            )

            if has_replacements:
                # HNSW does not support vector deletion. Rebuild the affected
                # tenant index so an upsert cannot leave stale vectors behind.
                retained = [
                    document
                    for existing in existing_by_vector_id.values()
                    if (document := dict(existing)).get("doc_id")
                    not in replacement_ids
                ]
                self._rebuild(
                    tenant,
                    retained + documents,
                )
                return

            matrix = self._embed(documents)
            start = (
                max(
                    (
                        int(key)
                        for key in existing_by_vector_id
                    ),
                    default=-1,
                )
                + 1
            )
            ids = np.arange(
                start,
                start + len(documents),
                dtype=np.int64,
            )
            index.add_with_ids(
                matrix,
                ids,
            )

            for vector_id, document in zip(
                ids.tolist(),
                documents,
            ):
                self.meta[tenant][
                    str(vector_id)
                ] = document

            self._persist(
                tenant,
                index,
                self.meta[tenant],
            )

    def search(
        self,
        tenant: str,
        query: str,
        limit: int = 8,
    ) -> list[Hit]:
        with self._lock:
            query_vector = np.asarray(
                self.embedder.embed([query]),
                dtype="float32",
            )
            self.faiss.normalize_L2(
                query_vector
            )

            index = self._load(tenant)
            if index.ntotal == 0:
                return []

            scores, ids = index.search(
                query_vector,
                limit,
            )
            hits = []

            for vector_id, score in zip(
                ids[0].tolist(),
                scores[0].tolist(),
            ):
                if vector_id < 0:
                    continue

                document = self.meta[tenant].get(
                    str(vector_id)
                )
                if document is None:
                    continue

                hits.append(
                    Hit(
                        doc_id=document["doc_id"],
                        title=document["title"],
                        tenant_id=tenant,
                        text=document["text"],
                        score=float(score),
                        source="vector",
                        metadata=document,
                    )
                )

            return hits

    def stats(self) -> dict:
        with self._lock:
            return {
                "backend": "FAISS HNSW",
                "tenants": {
                    tenant: int(index.ntotal)
                    for tenant, index in self.indexes.items()
                },
            }

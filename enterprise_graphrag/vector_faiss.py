from __future__ import annotations

import json
import re
import threading
from pathlib import Path

import numpy as np

from .embeddings import Embedder
from .fusion import Hit


class TenantFAISS:
    """One FAISS HNSW index per tenant; tenant isolation is physical."""

    def __init__(self, root: str, embedder: Embedder) -> None:
        import faiss

        self.faiss = faiss
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self.dimension = embedder.dimension
        self.indexes = {}
        self.meta = {}
        self._lock = threading.RLock()

    @staticmethod
    def _safe_tenant(tenant: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "_", tenant)

    def _paths(self, tenant: str):
        safe = self._safe_tenant(tenant)
        return (
            self.root / f"{safe}.faiss",
            self.root / f"{safe}.json",
        )

    def _load(self, tenant: str):
        with self._lock:
            if tenant in self.indexes:
                return self.indexes[tenant]

            index_path, meta_path = self._paths(tenant)
            if index_path.exists() and meta_path.exists():
                index = self.faiss.read_index(str(index_path))
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
                base = self.faiss.IndexHNSWFlat(
                    self.dimension,
                    32,
                    self.faiss.METRIC_INNER_PRODUCT,
                )
                base.hnsw.efConstruction = 80
                base.hnsw.efSearch = 64
                index = self.faiss.IndexIDMap2(base)
                self.meta[tenant] = {}

            self.indexes[tenant] = index
            return index

    def add(
        self,
        tenant: str,
        documents: list[dict],
    ) -> None:
        if not documents:
            return

        with self._lock:
            matrix = np.asarray(
                self.embedder.embed(
                    [
                        f"{doc['title']}
{doc['text']}"
                        for doc in documents
                    ]
                ),
                dtype="float32",
            )
            self.faiss.normalize_L2(matrix)

            index = self._load(tenant)
            start = (
                max(
                    (int(key) for key in self.meta[tenant]),
                    default=-1,
                )
                + 1
            )
            ids = np.arange(
                start,
                start + len(documents),
                dtype=np.int64,
            )
            index.add_with_ids(matrix, ids)

            for vector_id, doc in zip(
                ids.tolist(),
                documents,
            ):
                self.meta[tenant][str(vector_id)] = dict(doc)

            index_path, meta_path = self._paths(tenant)
            self.faiss.write_index(
                index,
                str(index_path),
            )
            meta_path.write_text(
                json.dumps(
                    self.meta[tenant],
                    indent=2,
                ),
                encoding="utf-8",
            )

    def search(
        self,
        tenant: str,
        query: str,
        limit: int = 8,
    ) -> list[Hit]:
        vector = np.asarray(
            self.embedder.embed([query]),
            dtype="float32",
        )
        self.faiss.normalize_L2(vector)

        index = self._load(tenant)
        if index.ntotal == 0:
            return []

        scores, ids = index.search(vector, limit)
        hits = []

        for vector_id, score in zip(
            ids[0].tolist(),
            scores[0].tolist(),
        ):
            if vector_id < 0:
                continue

            metadata = self.meta[tenant].get(
                str(vector_id)
            )
            if metadata is None:
                continue

            hits.append(
                Hit(
                    doc_id=metadata["doc_id"],
                    title=metadata["title"],
                    tenant_id=tenant,
                    text=metadata["text"],
                    score=float(score),
                    source="vector",
                    metadata=metadata,
                )
            )

        return hits

    def stats(self) -> dict:
        return {
            "backend": "FAISS HNSW",
            "tenants": {
                tenant: int(index.ntotal)
                for tenant, index in self.indexes.items()
            },
        }

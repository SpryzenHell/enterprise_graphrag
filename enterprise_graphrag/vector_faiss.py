from __future__ import annotations

from pathlib import Path
import json
import numpy as np


class TenantFAISS:
    """One FAISS HNSW index per tenant; no cross-tenant candidates."""
    def __init__(self, root: str, dimension: int = 384):
        import faiss
        self.faiss = faiss
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.dimension = dimension
        self.indexes = {}
        self.meta = {}

    def _load(self, tenant: str):
        if tenant in self.indexes:
            return self.indexes[tenant]
        path = self.root / f"{tenant}.faiss"
        meta = self.root / f"{tenant}.json"
        if path.exists():
            index = self.faiss.read_index(str(path))
            self.meta[tenant] = json.loads(meta.read_text())
        else:
            base = self.faiss.IndexHNSWFlat(self.dimension, 32, self.faiss.METRIC_INNER_PRODUCT)
            base.hnsw.efConstruction = 80
            base.hnsw.efSearch = 64
            index = self.faiss.IndexIDMap2(base)
            self.meta[tenant] = {}
        self.indexes[tenant] = index
        return index

    def add(self, tenant: str, vectors: list[list[float]], metadata: list[dict]):
        index = self._load(tenant)
        matrix = np.asarray(vectors, dtype="float32")
        self.faiss.normalize_L2(matrix)
        start = max([int(x) for x in self.meta[tenant]] or [-1]) + 1
        ids = np.arange(start, start + len(metadata), dtype="int64")
        index.add_with_ids(matrix, ids)
        for i, item in zip(ids, metadata):
            self.meta[tenant][str(int(i))] = item
        self.faiss.write_index(index, str(self.root / f"{tenant}.faiss"))
        (self.root / f"{tenant}.json").write_text(json.dumps(self.meta[tenant], indent=2))

    def search(self, tenant: str, vector: list[float], k: int = 8):
        index = self._load(tenant)
        if not index.ntotal:
            return []
        q = np.asarray([vector], dtype="float32")
        self.faiss.normalize_L2(q)
        scores, ids = index.search(q, k)
        return [(self.meta[tenant][str(int(i))], float(s)) for i, s in zip(ids[0], scores[0]) if int(i) >= 0]

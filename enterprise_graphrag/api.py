from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import require_query_access
from .config import settings
from .retrieval import HybridRetriever, TenantMemoryGraph
from .schemas import QueryRequest
from .security import SecurityGateway

app = FastAPI(title="Enterprise GraphRAG Agent", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8000"], allow_methods=["GET", "POST"], allow_headers=["Authorization", "Content-Type"])

security = SecurityGateway(threshold=settings.security_ppl_threshold, marker_threshold=settings.security_marker_threshold)
retriever = HybridRetriever(TenantMemoryGraph(), security)


@app.get("/health")
def health():
    return {"status": "ok", "retrieval": "hybrid-vector-graph-rrf", "security": "marker+ppl", "vllm_ppl_enabled": bool(settings.vllm_base_url and settings.vllm_model)}


@app.post("/v1/query")
def query(request: QueryRequest, principal: dict = Depends(require_query_access)):
    direct = security.inspect(request.query, direct=True)
    if not direct["allowed"]:
        return {"answer": "Request blocked by the security gateway.", "citations": [], "security": direct, "trace": {"blocked_stage": "input_policy"}}
    hits, blocked, vector_count, graph_count = retriever.search(principal["tenant_id"], request.query, request.top_k or settings.top_k)
    answer = hits[0].text if hits else "No authorized evidence found."
    return {
        "answer": answer,
        "citations": [{"rank": i, "doc_id": h.doc_id, "title": h.title, "tenant_id": h.tenant_id, "score": h.score, "source": h.source} for i, h in enumerate(hits, 1)],
        "security": {"allowed": True, "reason": "authorized evidence", "blocked_contexts": blocked},
        "trace": {"tenant_id": principal["tenant_id"], "vector_candidates": vector_count, "graph_candidates": graph_count, "fused_candidates": len(hits) + len(blocked)},
    }

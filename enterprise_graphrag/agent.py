from __future__ import annotations

from pathlib import Path
from .config import settings
from .embeddings import build_embedder
from .llm import build_answer_model
from .neo4j_store import Neo4jTenantStore
from .retrieval import HybridRetriever, TenantMemoryGraph
from .security import SecurityGateway
from .vector_faiss import TenantFAISS


class EnterpriseGraphRAGAgent:
    def __init__(self, retriever: HybridRetriever, answer_model) -> None:
        self.retriever = retriever
        self.answer_model = answer_model

    def query(
        self,
        principal,
        query: str,
        top_k: int | None = None,
    ) -> dict:
        direct = self.retriever.security.inspect(
            query,
            direct=True,
        )
        if not direct["allowed"]:
            return {
                "answer": "Request blocked by the security gateway.",
                "citations": [],
                "security": direct,
                "trace": {
                    "tenant_id": principal.tenant_id,
                    "blocked_stage": "input_policy",
                },
                "graph": {"nodes": [], "edges": []},
            }

        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")

        resolved_top_k = (
            settings.top_k
            if top_k is None
            else top_k
        )
        if resolved_top_k < 1 or resolved_top_k > 50:
            raise ValueError("top_k must be between 1 and 50")

        allowed, blocked, vector_count, graph_count = (
            self.retriever.search(
                principal.tenant_id,
                query,
                resolved_top_k,
            )
        )

        contexts = [
            {
                "doc_id": hit.doc_id,
                "title": hit.title,
                "text": hit.text,
            }
            for hit in allowed
        ]

        return {
            "answer": self.answer_model.answer(
                query,
                contexts,
            ),
            "citations": [
                {
                    "rank": rank,
                    "doc_id": hit.doc_id,
                    "title": hit.title,
                    "tenant_id": hit.tenant_id,
                    "score": hit.score,
                    "sources": hit.metadata.get(
                        "rrf_sources",
                        [hit.source],
                    ),
                    "snippet": hit.text[:500],
                }
                for rank, hit in enumerate(
                    allowed,
                    start=1,
                )
            ],
            "security": {
                "allowed": True,
                "reason": "authorized evidence",
                "marker_count": 0,
                "perplexity": None,
            },
            "trace": {
                "tenant_id": principal.tenant_id,
                "subject": principal.subject,
                "vector_candidates": vector_count,
                "graph_candidates": graph_count,
                "fused_candidates": len(allowed) + len(blocked),
                "blocked_contexts": blocked,
                "rrf_weights": {
                    "vector": self.retriever.vector_weight,
                    "graph": self.retriever.graph_weight,
                },
                "answer_model": type(self.answer_model).__name__,
            },
            "graph": self.retriever.trace(
                principal.tenant_id,
                [hit.doc_id for hit in allowed],
            ),
        }


def build_agent() -> EnterpriseGraphRAGAgent:
    vector = TenantFAISS(
        settings.faiss_dir,
        build_embedder(settings),
    )

    if settings.neo4j_uri and settings.neo4j_password:
        graph = Neo4jTenantStore(
            settings.neo4j_uri,
            settings.neo4j_user,
            settings.neo4j_password,
            settings.neo4j_database,
        )
        graph.verify()
        graph.ensure_schema()
    else:
        graph = TenantMemoryGraph(
            str(
                Path(settings.faiss_dir)
                / "memory_graph.json"
            )
        )

    security = SecurityGateway(
        base_url=settings.vllm_base_url,
        api_key=settings.vllm_api_key,
        model=settings.vllm_model,
        threshold=settings.security_ppl_threshold,
        marker_threshold=settings.security_marker_threshold,
    )

    retriever = HybridRetriever(
        vector=vector,
        graph=graph,
        security=security,
        vector_weight=settings.vector_weight,
        graph_weight=settings.graph_weight,
        rrf_k=settings.rrf_k,
    )

    return EnterpriseGraphRAGAgent(
        retriever=retriever,
        answer_model=build_answer_model(settings),
    )

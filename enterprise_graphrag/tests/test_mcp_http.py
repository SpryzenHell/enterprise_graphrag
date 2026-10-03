from pathlib import Path

from fastapi.testclient import TestClient

from enterprise_graphrag.agent import EnterpriseGraphRAGAgent
from enterprise_graphrag.api import create_app
from enterprise_graphrag.embeddings import HashEmbedder
from enterprise_graphraggraphrag.llm import ExtractiveAnswerModel
from enterprise_graphrag.retrieval import HybridRetriever, TenantMemoryGraph
from enterprise_graphrag.security import SecurityGateway
from enterprise_graphrag.vector_faiss import TenantFAISS


def build_test_app(tmp_path: Path):
    vector = TenantFAISS(
        str(tmp_path / "faiss"),
        HashEmbedder(32),
    )
    retriever = HybridRetriever(
        vector=vector,
        graph=TenantMemoryGraph(),
        security=SecurityGateway(),
        vector_weight=0.55,
        graph_weight=0.45,
        rrf_k=60,
    )
    agent = EnterpriseGraphRAGAgent(
        retriever,
        ExtractiveAnswerModel(),
    )
    return create_app(agent)


def test_mcp_http_route_requires_bearer_token(tmp_path):
    client = TestClient(
        build_test_app(tmp_path)
    )

    response = client.post(
        "/mcp/",
        headers={
            "Host": "localhost:8000",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        },
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {
                    "name": "ci-test",
                    "version": "0.1.0",
                },
            },
        },
    )

    assert response.status_code == 401

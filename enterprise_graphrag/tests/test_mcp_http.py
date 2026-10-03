from pathlib import Path

from fastapi.testclient import TestClient

from enterprise_graphrag.agent import EnterpriseGraphRAGAgent
from enterprise_graphrag.api import create_app
from enterprise_graphrag.auth import issue_demo_token
from enterprise_graphrag.embeddings import HashEmbedder
from enterprise_graphrag.llm import ExtractiveAnswerModel
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


def test_mcp_authenticated_tool_call_uses_jwt_tenant(tmp_path):
    token = issue_demo_token(
        "mcp-user",
        "acme",
        ["graphrag:query"],
    )

    # Seed data through the same supported retriever used by the API.
    vector = TenantFAISS(
        str(tmp_path / "mcp-fresh-faiss"),
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
    agent.retriever.add(
        "acme",
        [
            {
                "doc_id": "acme-mcp",
                "title": "Acme MCP Policy",
                "text": "Acme retains incident records for 365 days.",
            }
        ],
    )
    application = create_app(agent)

    with TestClient(application) as client:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "Mcp-Protocol-Version": "2025-06-18",
            "Host": "localhost:8000",
        }

        initialize = client.post(
            "/mcp/",
            headers=headers,
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
        assert initialize.status_code == 200
        initialize_body = initialize.json()
        assert initialize_body["result"]["protocolVersion"]

        initialized = client.post(
            "/mcp/",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            },
        )
        assert initialized.status_code in {200, 202}

        tools = client.post(
            "/mcp/",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {},
            },
        )
        assert tools.status_code == 200
        tool_names = [
            item["name"]
            for item in tools.json()["result"]["tools"]
        ]
        assert "hybrid_search" in tool_names

        call = client.post(
            "/mcp/",
            headers=headers,
            json={
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "hybrid_search",
                    "arguments": {
                        "query": "incident records",
                        "top_k": 5,
                    },
                },
            },
        )
        assert call.status_code == 200
        result = call.json()["result"]
        assert result.get("isError") is not True

        structured = result.get("structuredContent") or {}
        assert structured["trace"]["tenant_id"] == "acme"
        assert any(
            citation["tenant_id"] == "acme"
            for citation in structured["citations"]
        )
        assert any(
            citation["doc_id"] == "acme-mcp"
            for citation in structured["citations"]
        )

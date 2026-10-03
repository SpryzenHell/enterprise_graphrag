import time

import jwt
import pytest
from fastapi import HTTPException

from enterprise_graphrag.config import DEFAULT_DEV_JWT_SECRET, Settings

from enterprise_graphrag.auth import (
    issue_demo_token,
    principal_from_token,
)
from enterprise_graphrag.config import settings


def test_invalid_audience_is_rejected():
    token = jwt.encode(
        {
            "sub": "u",
            "tenant_id": "acme",
            "scope": "graphrag:query",
            "iss": settings.jwt_issuer,
            "aud": "wrong-audience",
        },
        settings.jwt_secret,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc:
        principal_from_token(token)

    assert exc.value.status_code == 401


def test_query_scope_is_preserved():
    token = issue_demo_token(
        "u",
        "acme",
        ["graphrag:query"],
    )
    principal = principal_from_token(token)
    assert principal.can("graphrag:query")
    assert not principal.can("graphrag:index")


def test_production_rejects_default_jwt_secret():
    config = Settings(
        environment="production",
        jwt_secret=DEFAULT_DEV_JWT_SECRET,
    )
    try:
        config.validate()
    except ValueError as exc:
        assert "GRAGRAPH_JWT_SECRET" in str(exc)
    else:
        raise AssertionError("production accepted the default JWT secret")


def test_partial_backend_configuration_is_rejected():
    config = Settings(
        environment="test",
        embedding_base_url="http://embedding.example",
        embedding_model="",
    )
    try:
        config.validate()
    except ValueError as exc:
        assert "EMBEDDING_BASE_URL" in str(exc)
    else:
        raise AssertionError("partial embedding configuration was accepted")


def test_negative_retrieval_weight_is_rejected():
    config = Settings(
        environment="test",
        vector_weight=-0.1,
        graph_weight=0.5,
    )
    try:
        config.validate()
    except ValueError as exc:
        assert "cannot be negative" in str(exc)
    else:
        raise AssertionError("negative retrieval weight was accepted")


def test_empty_mcp_allowlist_is_rejected():
    config = Settings(
        environment="test",
        mcp_allowed_hosts=(),
        mcp_allowed_origins=("http://localhost:*",),
    )
    try:
        config.validate()
    except ValueError as exc:
        assert "MCP_ALLOWED_HOSTS" in str(exc)
    else:
        raise AssertionError("empty MCP host allowlist was accepted")


def test_production_rejects_loopback_service_urls():
    config = Settings(
        environment="production",
        jwt_secret="ci-only-secret-change-me-please-32-bytes",
    )
    try:
        config.validate()
    except ValueError as exc:
        message = str(exc)
        assert "GRAGRAPH_JWT_ISSUER" in message
        assert "MCP_RESOURCE_URL" in message
        assert "MCP_ISSUER_URL" in message
    else:
        raise AssertionError("loopback production URLs were accepted")


def test_demo_token_cli_mints_token_in_test_mode(monkeypatch, capsys):
    import sys

    import enterprise_graphrag.token as token_cli

    monkeypatch.setattr(
        token_cli,
        "settings",
        Settings(environment="test"),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "enterprise-graphrag-token",
            "--subject",
            "cli-user",
            "--tenant",
            "acme",
        ],
    )

    token_cli.main()

    token_value = capsys.readouterr().out.strip()
    assert token_value
    principal = principal_from_token(token_value)
    assert principal.subject == "cli-user"
    assert principal.tenant_id == "acme"
    assert principal.can("graphrag:query")


def test_demo_token_cli_refuses_production(monkeypatch):
    import enterprise_graphrag.token as token_cli

    monkeypatch.setattr(
        token_cli,
        "settings",
        Settings(
            environment="production",
            jwt_secret="ci-only-secret-change-me-please-32-bytes",
            jwt_issuer="https://graphrag.example.invalid",
            mcp_resource_url="https://graphrag.example.invalid/mcp/",
            mcp_issuer_url="https://graphrag.example.invalid",
        ),
    )

    try:
        token_cli.main()
    except SystemExit as exc:
        assert "Refusing to mint" in str(exc)
    else:
        raise AssertionError("production demo-token minting was allowed")


def test_top_k_upper_bound_is_rejected():
    config = Settings(
        environment="test",
        top_k=51,
    )
    try:
        config.validate()
    except ValueError as exc:
        assert "TOP_K must be between 1 and 50" in str(exc)
    else:
        raise AssertionError("TOP_K above API limit was accepted")


def test_expired_token_is_rejected():
    token = jwt.encode(
        {
            "sub": "u",
            "tenant_id": "acme",
            "scope": "graphrag:query",
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "exp": int(time.time()) - 1,
        },
        settings.jwt_secret,
        algorithm="HS256",
    )

    with pytest.raises(HTTPException) as exc:
        principal_from_token(token)

    assert exc.value.status_code == 401


def test_api_scope_is_enforced():
    from fastapi.testclient import TestClient

    from enterprise_graphrag.agent import EnterpriseGraphRAGAgent
    from enterprise_graphrag.api import create_app
    from enterprise_graphrag.embeddings import HashEmbedder
    from enterprise_graphrag.llm import ExtractiveAnswerModel
    from enterprise_graphrag.retrieval import HybridRetriever, TenantMemoryGraph
    from enterprise_graphrag.security import SecurityGateway
    from enterprise_graphrag.vector_faiss import TenantFAISS

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as root:
        vector = TenantFAISS(str(Path(root) / "faiss"), HashEmbedder(32))
        agent = EnterpriseGraphRAGAgent(
            HybridRetriever(
                vector=vector,
                graph=TenantMemoryGraph(),
                security=SecurityGateway(),
                vector_weight=0.55,
                graph_weight=0.45,
                rrf_k=60,
            ),
            ExtractiveAnswerModel(),
        )
        client = TestClient(create_app(agent))
        token = issue_demo_token("u", "acme", ["other:scope"])

        response = client.post(
            "/v1/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": "policy"},
        )

        assert response.status_code == 403
        assert "graphrag:query" in response.json()["detail"]


def test_jwks_token_verification_uses_signing_key(monkeypatch):
    import jwt as pyjwt
    from cryptography.hazmat.primitives.asymmetric import rsa
    from enterprise_graphrag import auth as auth_module

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    token = pyjwt.encode(
        {
            "sub": "jwks-user",
            "tenant_id": "acme",
            "scope": "graphrag:query",
            "iss": "https://issuer.example",
            "aud": "enterprise-graphrag-api",
            "exp": int(time.time()) + 300,
        },
        private_key,
        algorithm="RS256",
        headers={"kid": "test-key"},
    )

    class FakeJWK:
        key = public_key

    class FakeClient:
        def __init__(self, url, **kwargs):
            assert url == "https://issuer.example/.well-known/jwks.json"

        def get_signing_key_from_jwt(self, supplied_token):
            assert supplied_token == token
            return FakeJWK()

    monkeypatch.setattr(auth_module, "PyJWKClient", FakeClient)
    auth_module._jwks_client.cache_clear()
    monkeypatch.setattr(
        auth_module,
        "settings",
        Settings(
            environment="test",
            jwt_mode="jwks",
            jwt_algorithm="RS256",
            jwt_secret="",
            jwt_jwks_url="https://issuer.example/.well-known/jwks.json",
            jwt_issuer="https://issuer.example",
            jwt_audience="enterprise-graphrag-api",
        ),
    )

    principal = auth_module.principal_from_token(token)
    assert principal.subject == "jwks-user"
    assert principal.tenant_id == "acme"
    assert principal.can("graphrag:query")


def test_jwks_configuration_requires_url():
    config = Settings(
        environment="test",
        jwt_mode="jwks",
        jwt_algorithm="RS256",
        jwt_secret="",
        jwt_jwks_url="",
    )
    with pytest.raises(ValueError, match="GRAGRAPH_JWT_JWKS_URL"):
        config.validate()


def test_jwks_mode_disables_demo_token_minting(monkeypatch):
    import enterprise_graphrag.auth as auth_module

    monkeypatch.setattr(
        auth_module,
        "settings",
        Settings(
            environment="test",
            jwt_mode="jwks",
            jwt_algorithm="RS256",
            jwt_secret="",
            jwt_jwks_url="https://issuer.example/.well-known/jwks.json",
            jwt_issuer="https://issuer.example",
        ),
    )

    with pytest.raises(RuntimeError, match="Demo tokens"):
        auth_module.issue_demo_token("u", "acme", ["graphrag:query"])


def test_production_rejects_wildcard_mcp_allowlists():
    config = Settings(
        environment="production",
        jwt_secret="ci-only-secret-change-me-please-32-bytes",
        jwt_issuer="https://issuer.example",
        mcp_resource_url="https://graphrag.example/mcp/",
        mcp_issuer_url="https://issuer.example",
        mcp_allowed_hosts=("*",),
        mcp_allowed_origins=("*",),
        allowed_origins=("*",),
    )
    with pytest.raises(ValueError) as exc:
        config.validate()
    message = str(exc.value)
    assert "MCP_ALLOWED_HOSTS" in message
    assert "MCP_ALLOWED_ORIGINS" in message
    assert "ALLOWED_ORIGINS" in message


def test_production_rejects_loopback_mcp_allowlists():
    config = Settings(
        environment="production",
        jwt_secret="ci-only-secret-change-me-please-32-bytes",
        jwt_issuer="https://issuer.example",
        mcp_resource_url="https://graphrag.example/mcp/",
        mcp_issuer_url="https://issuer.example",
        mcp_allowed_hosts=("localhost:*",),
        mcp_allowed_origins=("http://127.0.0.1:8000",),
    )
    with pytest.raises(ValueError) as exc:
        config.validate()
    message = str(exc.value)
    assert "MCP_ALLOWED_HOSTS" in message
    assert "MCP_ALLOWED_ORIGINS" in message

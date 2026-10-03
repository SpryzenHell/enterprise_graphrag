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

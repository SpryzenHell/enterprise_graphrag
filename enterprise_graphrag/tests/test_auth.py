import jwt
import pytest
from fastapi import HTTPException

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

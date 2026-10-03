from __future__ import annotations

from functools import lru_cache

import jwt
from fastapi import Depends, Header, HTTPException
from jwt import PyJWKClient

from .config import settings
from .schemas import TenantPrincipal


@lru_cache(maxsize=4)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_jwk_set=True, lifespan=300)


def _verification_key(token: str):
    if settings.jwt_mode == "jwks":
        return _jwks_client(settings.jwt_jwks_url).get_signing_key_from_jwt(token).key
    return settings.jwt_secret


def issue_demo_token(subject: str, tenant_id: str, scopes: list[str]) -> str:
    """Issue a local-development token; production should use the enterprise IdP."""
    if settings.jwt_mode != "shared_secret":
        raise RuntimeError("Demo tokens are only available in shared_secret mode")

    return jwt.encode(
        {
            "sub": subject,
            "tenant_id": tenant_id,
            "scope": " ".join(scopes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def principal_from_token(token: str) -> TenantPrincipal:
    try:
        payload = jwt.decode(
            token,
            _verification_key(token),
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "tenant_id", "iss", "aud"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"invalid access token: {exc}",
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=403, detail="token missing sub")

    tenant_id = payload.get("tenant_id")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise HTTPException(status_code=403, detail="token missing tenant_id")

    return TenantPrincipal(
        subject=subject,
        tenant_id=tenant_id,
        scopes=frozenset(str(payload.get("scope", "")).split()),
    )


async def require_query_access(
    authorization: str | None = Header(default=None),
) -> TenantPrincipal:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    principal = principal_from_token(authorization[7:])
    if not principal.can("graphrag:query"):
        raise HTTPException(
            status_code=403,
            detail="missing graphrag:query scope",
        )
    return principal

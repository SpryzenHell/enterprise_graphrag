from __future__ import annotations

import jwt
from fastapi import Depends, Header, HTTPException

from .config import settings
from .schemas import TenantPrincipal


def issue_demo_token(subject: str, tenant_id: str, scopes: list[str]) -> str:
    """Issue a local-development token; production should use the enterprise IdP."""
    return jwt.encode(
        {
            "sub": subject,
            "tenant_id": tenant_id,
            "scope": " ".join(scopes),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


def principal_from_token(token: str) -> TenantPrincipal:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=["HS256"],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "tenant_id", "iss", "aud"]},
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=401,
            detail=f"invalid access token: {exc}",
        ) from exc

    tenant_id = payload.get("tenant_id")
    if not isinstance(tenant_id, str) or not tenant_id:
        raise HTTPException(status_code=403, detail="token missing tenant_id")

    return TenantPrincipal(
        subject=str(payload["sub"]),
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

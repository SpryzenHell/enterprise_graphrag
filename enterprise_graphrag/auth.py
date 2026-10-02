from __future__ import annotations

import jwt
from fastapi import Depends, Header, HTTPException

from .config import settings


def issue_demo_token(subject: str, tenant_id: str, scopes: list[str]) -> str:
    return jwt.encode(
        {"sub": subject, "tenant_id": tenant_id, "scope": " ".join(scopes), "iss": settings.jwt_issuer, "aud": settings.jwt_audience},
        settings.jwt_secret,
        algorithm="HS256",
    )


def principal_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer, audience=settings.jwt_audience)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"invalid access token: {exc}") from exc
    tenant = payload.get("tenant_id")
    if not isinstance(tenant, str) or not tenant:
        raise HTTPException(status_code=403, detail="token missing tenant_id")
    return {"subject": str(payload["sub"]), "tenant_id": tenant, "scopes": frozenset(str(payload.get("scope", "")).split())}


async def require_query_access(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    principal = principal_from_token(authorization[7:])
    if "graphrag:query" not in principal["scopes"] and "*" not in principal["scopes"]:
        raise HTTPException(status_code=403, detail="missing graphrag:query scope")
    return principal

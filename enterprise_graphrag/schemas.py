from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class TenantPrincipal:
    subject: str
    tenant_id: str
    scopes: frozenset[str] = field(default_factory=frozenset)

    def can(self, scope: str) -> bool:
        return "*" in self.scopes or scope in self.scopes


class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=4000)
    top_k: int | None = Field(default=None, ge=1, le=50)


class Citation(BaseModel):
    rank: int
    doc_id: str
    title: str
    tenant_id: str
    score: float
    sources: list[str]
    snippet: str


class SecurityDecision(BaseModel):
    allowed: bool
    reason: str
    marker_count: int
    perplexity: float | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    security: SecurityDecision
    trace: dict[str, Any]
    graph: dict[str, Any]


def validate_documents(
    tenant_id: str,
    documents: list[dict],
) -> list[dict]:
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise ValueError("tenant_id must be a non-empty string")

    normalized: dict[str, dict] = {}
    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("each document must be an object")

        doc_id = document.get("doc_id")
        title = document.get("title")
        text = document.get("text")

        if not isinstance(doc_id, str) or not doc_id.strip():
            raise ValueError("document doc_id must be a non-empty string")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                f"document {doc_id!r} title must be a non-empty string"
            )
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"document {doc_id!r} text must be a non-empty string"
            )

        embedded_tenant = document.get("tenant_id")
        if (
            embedded_tenant is not None
            and embedded_tenant != tenant_id
        ):
            raise ValueError(
                f"document {doc_id!r} tenant_id does not match target tenant"
            )

        normalized_doc = dict(document)
        normalized_doc.pop(
            "tenant_id",
            None,
        )
        normalized[doc_id] = normalized_doc

    return list(normalized.values())

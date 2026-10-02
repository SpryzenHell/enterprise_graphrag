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

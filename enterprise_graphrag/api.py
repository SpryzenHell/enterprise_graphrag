from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse

from .agent import EnterpriseGraphRAGAgent, build_agent
from .auth import require_query_access
from .config import settings
from .schemas import QueryRequest, QueryResponse, TenantPrincipal


def create_app(agent: EnterpriseGraphRAGAgent | None = None) -> FastAPI:
    runtime = agent or build_agent()
    mcp = None
    mcp_app = None

    try:
        from .mcp_server import create_mcp_server
        mcp = create_mcp_server(runtime)
        mcp_app = mcp.streamable_http_app(
            streamable_http_path="/",
            json_response=True,
            stateless_http=True,
            host="127.0.0.1",
        )
    except (ImportError, RuntimeError):
        mcp = None
        mcp_app = None

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        if mcp is not None:
            async with mcp.session_manager.run():
                yield
        else:
            yield

    app = FastAPI(
        title="Enterprise GraphRAG Agent",
        version="0.2.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Mcp-Session-Id",
            "Mcp-Protocol-Version",
        ],
        expose_headers=["Mcp-Session-Id"],
    )

    @app.get("/")
    def home() -> HTMLResponse:
        return HTMLResponse(
            "<h1>Enterprise GraphRAG</h1>"
            "<p>Use <a href='/docs'>/docs</a> or POST /v1/query.</p>"
        )

    @app.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "retrieval": "FAISS HNSW + graph + weighted RRF",
            "graph_backend": type(
                runtime.retriever.graph
            ).__name__,
            "vector_backend": type(
                runtime.retriever.vector
            ).__name__,
            "answer_backend": type(
                runtime.answer_model
            ).__name__,
            "mcp_enabled": mcp_app is not None,
            "vllm_enabled": bool(
                settings.vllm_base_url
                and settings.vllm_model
            ),
        }

    @app.get("/v1/tenant")
    def tenant(
        principal: TenantPrincipal = Depends(
            require_query_access
        ),
    ) -> dict:
        return {
            "subject": principal.subject,
            "tenant_id": principal.tenant_id,
            "scopes": sorted(principal.scopes),
        }

    @app.post(
        "/v1/query",
        response_model=QueryResponse,
    )
    def query(
        request: QueryRequest,
        principal: TenantPrincipal = Depends(
            require_query_access
        ),
    ) -> QueryResponse:
        return QueryResponse.model_validate(
            runtime.query(
                principal,
                request.query,
                request.top_k,
            )
        )

    if mcp_app is not None:
        app.mount("/mcp", mcp_app)

    return app


app = create_app()

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from mcp.server.transport_security import (
    TransportSecuritySettings,
)

from .agent import EnterpriseGraphRAGAgent, build_agent
from .auth import require_query_access
from .config import settings
from .errors import BackendUnavailable
from .schemas import QueryRequest, QueryResponse, TenantPrincipal


UI_PATH = Path(__file__).with_name("static").joinpath(
    "index.html"
)


def create_app(
    agent: EnterpriseGraphRAGAgent | None = None,
) -> FastAPI:
    runtime = agent or build_agent()
    mcp = None
    mcp_app = None

    from .mcp_server import create_mcp_server

    mcp = create_mcp_server(runtime)
    mcp_app = mcp.streamable_http_app(
        streamable_http_path="/",
        json_response=True,
        stateless_http=True,
        host="0.0.0.0",
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=list(
                settings.mcp_allowed_hosts
            ),
            allowed_origins=list(
                settings.mcp_allowed_origins
            ),
        ),
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        try:
            if mcp is not None:
                async with mcp.session_manager.run():
                    yield
            else:
                yield
        finally:
            close = getattr(
                runtime.retriever.graph,
                "close",
                None,
            )
            if close is not None:
                close()

    application = FastAPI(
        title="Enterprise GraphRAG Agent",
        version="0.2.0",
        lifespan=lifespan,
    )

    @application.middleware("http")
    async def operational_headers(
        request: Request,
        call_next,
    ):
        request_id = uuid4().hex
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        return response
    application.add_middleware(
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

    @application.exception_handler(BackendUnavailable)
    async def backend_unavailable(
        _request: Request,
        exc: BackendUnavailable,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": str(exc),
                "status": "backend_unavailable",
            },
        )

    @application.get(
        "/",
        response_class=HTMLResponse,
    )
    def home() -> HTMLResponse:
        return HTMLResponse(
            UI_PATH.read_text(
                encoding="utf-8"
            )
        )

    @application.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "retrieval": (
                "FAISS HNSW + graph + weighted RRF"
            ),
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

    @application.get("/ready")
    def ready() -> dict:
        graph = runtime.retriever.graph
        verify = getattr(
            graph,
            "verify",
            None,
        )
        if verify is not None:
            try:
                verify()
            except Exception as exc:
                raise HTTPException(
                    status_code=503,
                    detail="Graph backend is not ready",
                ) from exc

        return {
            "status": "ready",
            "graph_backend": type(
                graph
            ).__name__,
            "vector_backend": type(
                runtime.retriever.vector
            ).__name__,
            "mcp_enabled": mcp_app is not None,
        }

    @application.get("/v1/tenant")
    def tenant(
        principal: TenantPrincipal = Depends(
            require_query_access
        ),
    ) -> dict:
        return {
            "subject": principal.subject,
            "tenant_id": principal.tenant_id,
            "scopes": sorted(
                principal.scopes
            ),
        }

    @application.post(
        "/v1/query",
        response_model=QueryResponse,
    )
    def query(
        request: QueryRequest,
        http_request: Request,
        principal: TenantPrincipal = Depends(
            require_query_access
        ),
    ) -> QueryResponse:
        result = runtime.query(
            principal,
            request.query,
            request.top_k,
        )
        result["trace"]["request_id"] = getattr(
            http_request.state,
            "request_id",
            "",
        )
        return QueryResponse.model_validate(result)

    if mcp_app is not None:
        application.mount(
            "/mcp",
            mcp_app,
        )

    return application


app = create_app()

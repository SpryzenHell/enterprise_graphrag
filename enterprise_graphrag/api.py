from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .agent import EnterpriseGraphRAGAgent, build_agent
from .auth import require_query_access
from .config import settings
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
        application.mount(
            "/mcp",
            mcp_app,
        )

    return application


app = create_app()

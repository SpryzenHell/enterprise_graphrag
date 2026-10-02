from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    jwt_secret: str = os.getenv("GRAGRAPH_JWT_SECRET", "dev-only-change-me")
    jwt_issuer: str = os.getenv("GRAGRAPH_JWT_ISSUER", "enterprise-graphrag")
    jwt_audience: str = os.getenv("GRAGRAPH_JWT_AUDIENCE", "enterprise-graphrag-api")
    faiss_dir: str = os.getenv("GRAGRAPH_FAISS_DIR", "./enterprise_data/faiss")
    neo4j_uri: str = os.getenv("NEO4J_URI", "")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
    neo4j_database: str = os.getenv("NEO4J_DATABASE", "neo4j")
    vllm_base_url: str = os.getenv("VLLM_BASE_URL", "").rstrip("/")
    vllm_api_key: str = os.getenv("VLLM_API_KEY", "dev-token")
    vllm_model: str = os.getenv("VLLM_MODEL", "")
    embedding_base_url: str = os.getenv("EMBEDDING_BASE_URL", "").rstrip("/")
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "dev-token")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")
    security_ppl_threshold: float = float(os.getenv("SECURITY_PPL_THRESHOLD", "80"))
    security_marker_threshold: int = int(os.getenv("SECURITY_MARKER_THRESHOLD", "2"))
    rrf_k: int = int(os.getenv("RRF_K", "60"))
    vector_weight: float = float(os.getenv("VECTOR_WEIGHT", "0.55"))
    graph_weight: float = float(os.getenv("GRAPH_WEIGHT", "0.45"))
    top_k: int = int(os.getenv("TOP_K", "8"))


settings = Settings()

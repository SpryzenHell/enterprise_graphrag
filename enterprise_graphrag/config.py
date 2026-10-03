from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


DEFAULT_DEV_JWT_SECRET = "dev-only-change-me-please-use-32-bytes!"


def _csv(value: str) -> tuple[str, ...]:
    return tuple(
        item.strip()
        for item in value.split(",")
        if item.strip()
    )


def _hostname(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv(
        "GRAGRAPH_ENV",
        "development",
    )

    jwt_mode: str = os.getenv(
        "GRAGRAPH_JWT_MODE",
        "shared_secret",
    )
    jwt_algorithm: str = os.getenv(
        "GRAGRAPH_JWT_ALGORITHM",
        "HS256",
    )
    jwt_secret: str = os.getenv(
        "GRAGRAPH_JWT_SECRET",
        DEFAULT_DEV_JWT_SECRET,
    )
    jwt_jwks_url: str = os.getenv(
        "GRAGRAPH_JWT_JWKS_URL",
        "",
    )
    jwt_issuer: str = os.getenv(
        "GRAGRAPH_JWT_ISSUER",
        "http://127.0.0.1:8000",
    )
    jwt_audience: str = os.getenv(
        "GRAGRAPH_JWT_AUDIENCE",
        "enterprise-graphrag-api",
    )

    faiss_dir: str = os.getenv(
        "GRAGRAPH_FAISS_DIR",
        "./enterprise_data/faiss",
    )
    corpus_path: str = os.getenv(
        "GRAGRAPH_CORPUS",
        "./enterprise_data/corpus.jsonl",
    )

    neo4j_uri: str = os.getenv(
        "NEO4J_URI",
        "",
    )
    neo4j_user: str = os.getenv(
        "NEO4J_USER",
        "neo4j",
    )
    neo4j_password: str = os.getenv(
        "NEO4J_PASSWORD",
        "",
    )
    neo4j_database: str = os.getenv(
        "NEO4J_DATABASE",
        "neo4j",
    )

    embedding_base_url: str = os.getenv(
        "EMBEDDING_BASE_URL",
        "",
    ).rstrip("/")
    embedding_api_key: str = os.getenv(
        "EMBEDDING_API_KEY",
        "dev-token",
    )
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "",
    )
    embedding_dimension: int = int(
        os.getenv(
            "EMBEDDING_DIMENSION",
            "384",
        )
    )

    vllm_base_url: str = os.getenv(
        "VLLM_BASE_URL",
        "",
    ).rstrip("/")
    vllm_api_key: str = os.getenv(
        "VLLM_API_KEY",
        "dev-token",
    )
    vllm_model: str = os.getenv(
        "VLLM_MODEL",
        "",
    )

    mcp_resource_url: str = os.getenv(
        "MCP_RESOURCE_URL",
        "http://127.0.0.1:8000/mcp/",
    )
    mcp_issuer_url: str = os.getenv(
        "MCP_ISSUER_URL",
        "http://127.0.0.1:8000",
    )
    mcp_allowed_hosts: tuple[str, ...] = _csv(
        os.getenv(
            "MCP_ALLOWED_HOSTS",
            "127.0.0.1:*,localhost:*,[::1]:*",
        )
    )
    mcp_allowed_origins: tuple[str, ...] = _csv(
        os.getenv(
            "MCP_ALLOWED_ORIGINS",
            "http://127.0.0.1:8000,http://localhost:8000",
        )
    )

    security_ppl_threshold: float = float(
        os.getenv(
            "SECURITY_PPL_THRESHOLD",
            "80",
        )
    )
    security_marker_threshold: int = int(
        os.getenv(
            "SECURITY_MARKER_THRESHOLD",
            "2",
        )
    )

    rrf_k: int = int(
        os.getenv(
            "RRF_K",
            "60",
        )
    )
    vector_weight: float = float(
        os.getenv(
            "VECTOR_WEIGHT",
            "0.55",
        )
    )
    graph_weight: float = float(
        os.getenv(
            "GRAPH_WEIGHT",
            "0.45",
        )
    )
    top_k: int = int(
        os.getenv(
            "TOP_K",
            "8",
        )
    )

    allowed_origins: tuple[str, ...] = _csv(
        os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8000",
        )
    )

    def validate(self) -> None:
        """Fail fast on deployment settings that can break correctness or auth."""
        problems: list[str] = []

        env = self.environment.strip().lower()
        if env not in {"development", "test", "production"}:
            problems.append(
                "GRAGRAPH_ENV must be development, test, or production"
            )

        allowed_jwt_modes = {"shared_secret", "jwks"}
        asymmetric_algorithms = {
            "RS256", "RS384", "RS512",
            "PS256", "PS384", "PS512",
            "ES256", "ES384", "ES512",
            "EdDSA",
        }
        if self.jwt_mode not in allowed_jwt_modes:
            problems.append("GRAGRAPH_JWT_MODE must be shared_secret or jwks")

        if self.jwt_mode == "shared_secret":
            if not self.jwt_secret:
                problems.append("GRAGRAPH_JWT_SECRET is required in shared_secret mode")
            if self.jwt_algorithm not in {"HS256", "HS384", "HS512"}:
                problems.append(
                    "GRAGRAPH_JWT_ALGORITHM must be HS256, HS384, or HS512 in shared_secret mode"
                )
            elif env == "production" and (
                self.jwt_secret == DEFAULT_DEV_JWT_SECRET
                or len(self.jwt_secret) < 32
            ):
                problems.append(
                    "GRAGRAPH_JWT_SECRET must be a non-default value of at least 32 characters in production"
                )
        elif self.jwt_algorithm not in asymmetric_algorithms:
            problems.append(
                "GRAGRAPH_JWT_ALGORITHM must be an asymmetric signing algorithm in jwks mode"
            )

        if not self.jwt_issuer:
            problems.append("GRAGRAPH_JWT_ISSUER is required")
        if not self.jwt_audience:
            problems.append("GRAGRAPH_JWT_AUDIENCE is required")
        if self.jwt_mode == "jwks" and not self.jwt_jwks_url:
            problems.append("GRAGRAPH_JWT_JWKS_URL is required in jwks mode")
        jwks_parsed = urlparse(self.jwt_jwks_url)
        jwks_host = _hostname(self.jwt_jwks_url)
        if self.jwt_jwks_url and env == "production" and (
            jwks_parsed.scheme != "https"
            or not jwks_host
            or jwks_host in {"localhost", "127.0.0.1", "::1"}
        ):
            problems.append(
                "GRAGRAPH_JWT_JWKS_URL must be an externally reachable HTTPS URL in production"
            )

        jwt_issuer_parsed = urlparse(self.jwt_issuer)
        jwt_issuer_host = _hostname(self.jwt_issuer)
        if env == "production" and (
            jwt_issuer_parsed.scheme not in {"http", "https"}
            or not jwt_issuer_host
            or jwt_issuer_host in {"localhost", "127.0.0.1", "::1"}
        ):
            problems.append(
                "GRAGRAPH_JWT_ISSUER must be an externally reachable HTTP(S) issuer in production"
            )

        if self.embedding_dimension <= 0:
            problems.append("EMBEDDING_DIMENSION must be greater than zero")

        if bool(self.embedding_base_url) != bool(self.embedding_model):
            problems.append(
                "EMBEDDING_BASE_URL and EMBEDDING_MODEL must be set together"
            )

        if bool(self.vllm_base_url) != bool(self.vllm_model):
            problems.append(
                "VLLM_BASE_URL and VLLM_MODEL must be set together"
            )

        if bool(self.neo4j_uri) != bool(self.neo4j_password):
            problems.append(
                "NEO4J_URI and NEO4J_PASSWORD must be set together"
            )

        if self.security_ppl_threshold <= 0:
            problems.append(
                "SECURITY_PPL_THRESHOLD must be greater than zero"
            )
        if self.security_marker_threshold <= 0:
            problems.append(
                "SECURITY_MARKER_THRESHOLD must be greater than zero"
            )
        if self.rrf_k <= 0:
            problems.append("RRF_K must be greater than zero")
        if self.top_k < 1 or self.top_k > 50:
            problems.append("TOP_K must be between 1 and 50")
        if self.vector_weight < 0 or self.graph_weight < 0:
            problems.append(
                "VECTOR_WEIGHT and GRAPH_WEIGHT cannot be negative"
            )
        if self.vector_weight + self.graph_weight <= 0:
            problems.append(
                "VECTOR_WEIGHT + GRAPH_WEIGHT must be greater than zero"
            )

        if not self.mcp_resource_url:
            problems.append("MCP_RESOURCE_URL is required")
        if not self.mcp_issuer_url:
            problems.append("MCP_ISSUER_URL is required")
        mcp_resource_host = _hostname(
            self.mcp_resource_url
        )
        mcp_resource_parsed = urlparse(
            self.mcp_resource_url
        )
        if env == "production" and (
            mcp_resource_parsed.scheme not in {"http", "https"}
            or not mcp_resource_host
            or mcp_resource_host in {"localhost", "127.0.0.1", "::1"}
        ):
            problems.append(
                "MCP_RESOURCE_URL must be an externally reachable HTTP(S) URL in production"
            )
        mcp_issuer_host = _hostname(
            self.mcp_issuer_url
        )
        mcp_issuer_parsed = urlparse(
            self.mcp_issuer_url
        )
        if env == "production" and (
            mcp_issuer_parsed.scheme not in {"http", "https"}
            or not mcp_issuer_host
            or mcp_issuer_host in {"localhost", "127.0.0.1", "::1"}
        ):
            problems.append(
                "MCP_ISSUER_URL must be an externally reachable HTTP(S) URL in production"
            )
        if not self.mcp_allowed_hosts:
            problems.append("MCP_ALLOWED_HOSTS must contain at least one host")
        if not self.mcp_allowed_origins:
            problems.append("MCP_ALLOWED_ORIGINS must contain at least one origin")

        if problems:
            raise ValueError(
                "Invalid Enterprise GraphRAG configuration: "
                + "; ".join(problems)
            )


settings = Settings()
settings.validate()

# Security

## Supported runtime

The supported application is under `enterprise_graphrag/`.

Its security boundary is:

    JWT authentication
        -> tenant identity
        -> tenant-scoped FAISS + Neo4j retrieval
        -> retrieval security gateway
        -> answer generation
        -> citations / graph trace

The retained legacy GraphRAG, MCP CLI and ACE-derived trees are not the supported production entrypoint.

## Authentication

Production should use an enterprise identity provider with asymmetric JWT signing and a JWKS endpoint:

    GRAGRAPH_JWT_MODE=jwks
    GRAGRAPH_JWT_ALGORITHM=RS256
    GRAGRAPH_JWT_ISSUER=https://<issuer>
    GRAGRAPH_JWT_AUDIENCE=<audience>
    GRAGRAPH_JWT_JWKS_URL=https://<issuer>/.well-known/jwks.json

Tokens must contain:

- `sub`
- `tenant_id`
- `iss`
- `aud`
- `exp`

All data-bearing API and MCP operations also require `graphrag:query`.

The local shared-secret mode and demo-token CLI are intended for development/test only.

## Tenant isolation

Tenant identity is derived from the verified token rather than from query or MCP tool arguments.

FAISS uses a physically separate index per tenant. Neo4j documents and entities carry tenant identity, and retrieval queries include explicit tenant predicates.

The deterministic test suite includes API, vector, graph and MCP cross-tenant regression tests.

## Retrieved-content security

Retrieved titles and document text are screened before answer generation.

The gateway normalizes Unicode compatibility characters and strips zero-width formatting before marker detection. When a vLLM endpoint is configured, observed-token prompt logprobs can supply an additional perplexity signal.

This is a defense-in-depth control, not a proof that arbitrary prompt injection is impossible.

## Deployment recommendations

Keep vLLM private whenever possible. On an HPC/DGX environment, bind vLLM to loopback and use SSH port forwarding through the required VPN/login path rather than exposing an inference port publicly.

Use a strong secret only for shared-secret development/test environments. Do not commit `.env` files or provider credentials.

Keep MCP allowed hosts and origins explicit in production. The configuration validator rejects wildcard and loopback MCP/CORS entries in production.

## Reporting a security issue

Do not open a public issue containing a credential, private dataset, token, vulnerability proof that exposes sensitive information, or other secret material.

For an actual deployment, use the repository owner's private security-reporting process or the organization security contact.

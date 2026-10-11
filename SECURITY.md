# Security

## Request flow

The application uses this security path:

    JWT authentication
        -> tenant identity
        -> tenant-scoped FAISS / Neo4j retrieval
        -> retrieval security checks
        -> answer generation
        -> citations and graph trace

## Authentication

For production, use an identity provider with asymmetric JWT signing and a JWKS endpoint:

    GRAGRAPH_JWT_MODE=jwks
    GRAGRAPH_JWT_ALGORITHM=RS256
    GRAGRAPH_JWT_ISSUER=https://<issuer>
    GRAGRAPH_JWT_AUDIENCE=<audience>
    GRAGRAPH_JWT_JWKS_URL=https://<issuer>/.well-known/jwks.json

Data-bearing requests require these token claims:

- `sub`
- `tenant_id`
- `iss`
- `aud`
- `exp`
- `graphrag:query` scope

Shared-secret JWT mode and the demo-token command are for development and tests.

## Tenant isolation

The tenant is taken from the verified token. It is not accepted from the query body or MCP tool arguments.

FAISS keeps a separate index for each tenant. Neo4j stores tenant identity on documents and entities and uses tenant filters in retrieval and trace queries.

The test suite checks cross-tenant access through the API, vector search, graph search and MCP.

## Retrieved text security

Document titles and text are checked before they reach the answer model.

The security layer:

- normalizes Unicode text;
- removes zero-width characters;
- checks for common instruction override and prompt-exfiltration phrases;
- blocks direct malicious queries;
- blocks retrieved text that reaches the configured marker threshold;
- can use prompt-token logprobs from vLLM as an additional signal;
- can use an optional semantic prompt-injection classifier to catch markerless indirect attacks.

To enable the optional semantic classifier, install the security extra and configure the Apache-2.0 `Horizon-Labs/prompt-injection-guard-small` checkpoint:

    pip install -e ".[security]"
    SECURITY_CLASSIFIER_MODEL=Horizon-Labs/prompt-injection-guard-small
    SECURITY_CLASSIFIER_THRESHOLD=0.5
    SECURITY_CLASSIFIER_MAX_LENGTH=8192
    SECURITY_CLASSIFIER_DEVICE=auto

The classifier is disabled when `SECURITY_CLASSIFIER_MODEL` is empty. When explicitly enabled, a model-load or inference error blocks the inspected item rather than silently reverting to marker-only checks. `auto` uses GPU 1 if more than one CUDA device is available (to avoid collocating with vLLM on GPU 0), otherwise it chooses the available GPU or CPU. A threshold is not a universal safety guarantee and must be validated against representative benign and malicious documents before production use.

The prompt-logprob check is an extra safety layer. In this implementation, a high PPL result only blocks when at least one injection marker is also present; markerless attacks therefore require the optional semantic classifier or another dedicated detector. No single detector proves that every prompt injection will be detected.

## Deployment

Keep vLLM private when possible. On an HPC system, bind it to loopback and use SSH port forwarding through the required VPN/login path.

Do not commit:

- `.env` files;
- JWTs;
- API keys;
- runner registration tokens;
- SSH private keys.

Production configuration rejects wildcard or loopback MCP/CORS settings.

## Reporting

Do not open a public issue with a secret, private dataset, token, or other sensitive material. Use the repository owner's private security contact for a real deployment issue.

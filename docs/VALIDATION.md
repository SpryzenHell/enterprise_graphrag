# Validation

This file records what has been validated in the repository and what still requires real infrastructure.

## Deterministic validation

The CI workflow runs:

1. Python compilation of the supported package and scripts.
2. Unit tests for JWT authorization, tenant isolation, FAISS integration, RRF, prompt-injection filtering and API behavior.
3. Backend contract tests for vLLM request construction, vLLM prompt-logprob PPL parsing and Neo4j tenant predicates.
4. A deterministic evaluation against a two-tenant fixture.

These checks are designed to run without a live Neo4j or vLLM service.

## Real-backend validation still required

Before describing the project as production-deployed or putting performance/security metrics on a resume, run the same workflow against:

- the target Neo4j version and dataset;
- the actual FAISS corpus and embedding model;
- the actual vLLM model and server configuration;
- representative benign and indirect-injection corpora.

Record Recall@K, MRR/nDCG, end-to-end latency, throughput, and security detection/false-positive rates from those runs. Do not derive those numbers from the small deterministic fixture.


## Real inference provider probe

Use the provider probe against the target OpenAI-compatible endpoint:

    python scripts/provider_probe.py \
      --base-url "$VLLM_BASE_URL" \
      --api-key "$VLLM_API_KEY" \
      --chat-model "$VLLM_MODEL" \
      --embedding-model "$EMBEDDING_MODEL" \
      --embedding-dimension "$EMBEDDING_DIMENSION"

The provider key is optional for a private/local vLLM server. The probe verifies Chat Completions, Embeddings, and prompt-logprob support, including observed-token logprobs and the configured embedding dimension. It reports per-operation latency but does not replace an application-level accuracy/security evaluation.

For a VPN-only HPC/DGX deployment, see [HPC_VLLM.md](HPC_VLLM.md) for the private same-node and SSH port-forwarding setup.

## Application runtime probe

After the service is running:

    python scripts/runtime_probe.py \
      --base-url "$GRAGRAPH_BASE_URL" \
      --token "$ENTERPRISE_IDP_ACCESS_TOKEN" \
      --tenant "$TENANT_ID" \
      --query "representative question"

This verifies liveness, readiness, authenticated tenant context, and that returned citations do not cross the supplied tenant boundary.


## Authenticated MCP probe

After the API is running and the same tenant JWT is available:

    python scripts/mcp_probe.py \
      --url "$GRAGRAPH_BASE_URL/mcp/" \
      --token "$ENTERPRISE_IDP_ACCESS_TOKEN" \
      --tenant "$TENANT_ID" \
      --query "representative question"

The probe verifies MCP initialization, tool discovery, authenticated `hybrid_search`, JWT-derived tenant identity, citation tenant isolation, and an optional expected document.

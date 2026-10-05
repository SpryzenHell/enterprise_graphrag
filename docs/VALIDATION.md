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

    export VLLM_API_KEY="<generation-key-or-empty>"
    export EMBEDDING_API_KEY="<embedding-key-or-empty>"
    python scripts/provider_probe.py \
      --base-url "$VLLM_BASE_URL" \
      --chat-model "$VLLM_MODEL" \
      --embedding-model "$EMBEDDING_MODEL" \
      --embedding-dimension "$EMBEDDING_DIMENSION"

Provider keys are read from `VLLM_API_KEY` and `EMBEDDING_API_KEY`; both are optional for local unauthenticated services. The probe verifies Chat Completions, Embeddings, and prompt-logprob support, including observed-token logprobs and the configured embedding dimension. It reports per-operation latency but does not replace an application-level accuracy/security evaluation.

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


## GPU validation

The self-hosted GPU workflow is separate from the normal CI workflow. It targets a runner labeled `gpu-a100` and validates the following on the allocated A100 node:

- CUDA visibility through `nvidia-smi` and PyTorch;
- vLLM model discovery;
- Chat Completions;
- prompt-token logprobs;
- optional Embeddings, including vector dimension and finite values;
- the normal deterministic test suite;
- an end-to-end GraphRAG query using the live vLLM answer backend;
- tenant isolation and retrieved-content injection blocking.

The workflow writes `gpu-validation.json` and a JUnit report as GitHub Actions artifacts.

For the current HPC environment, the network bootstrap must happen before the runner process starts:

    source "$HOME/Conda/bin/activate"
    python -c "import core_config"

The repository provides `scripts/start_hpc_runner.sh`, which performs this bootstrap before starting the runner from:

    ~/gpu/actions-runner-enterprise-graphrag

The GPU workflow is intentionally owner-gated and does not run on pull requests.

## Interpreting evidence

The deterministic benchmark currently contains four labeled questions and is useful for detecting regressions in the checked-in retrieval fixture. The fixture analysis also sweeps retrieval depth and RRF weights and records the tenant-isolation and injection-filtering cases. It should not be used to represent production retrieval quality.

The real provider and GPU probes report protocol success and operation latency. They do not establish model quality on an arbitrary corpus.

Production measurements should be recorded separately for the target model, embedding model, corpus, Neo4j deployment and security test set. Keep the configuration used for each measurement with the resulting evidence so that later comparisons remain meaningful.

# Enterprise GraphRAG

<p align="center">
  <img src="main.png" alt="Enterprise GraphRAG project overview" width="900">
</p>

Enterprise GraphRAG is a tenant-scoped retrieval service that combines vector search, graph retrieval and a retrieval-time security boundary behind a small FastAPI application.

The supported implementation is in `enterprise_graphrag/`. The older GraphRAG, MCP and ACE-derived directories are retained in the repository for provenance, but they are not required by the supported runtime.

[![CI](https://github.com/SpryzenHell/enterprise_graphrag/actions/workflows/enterprise-graphrag.yml/badge.svg)](https://github.com/SpryzenHell/enterprise_graphrag/actions/workflows/enterprise-graphrag.yml)

## What is included

| Area | Supported implementation |
| --- | --- |
| API | FastAPI |
| Authentication | JWT with issuer/audience validation and required tenant identity |
| Tenant isolation | Token-derived tenant context, tenant-partitioned FAISS, tenant-aware Neo4j |
| Vector retrieval | FAISS HNSW with normalized embeddings |
| Graph retrieval | In-memory graph for local use; Neo4j adapter for shared deployment |
| Ranking | Weighted Reciprocal Rank Fusion |
| Retrieval security | Unicode normalization, injection markers, optional vLLM prompt-logprob signal |
| Answer generation | Deterministic extractive model or vLLM |
| Tool protocol | MCP Streamable HTTP with bearer-token verification |
| UI | Small browser UI served by the API |
| Ingestion | Streaming JSONL ingestion with tenant validation and upsert semantics |
| Packaging | Python package and production Docker image |
| Validation | Unit tests, Neo4j integration, security evaluation, retrieval benchmark, runtime probes |
| GPU validation | Optional private A100 self-hosted GitHub Actions workflow |

## Architecture

The request path is:

```
Client
  |
  v
FastAPI
  |
  +--> JWT validation --> tenant context
  |
  +--> FAISS HNSW --------+
  |                       |
  +--> graph retrieval ---+--> weighted RRF
                              |
                              v
                       retrieval security
                              |
                              v
                     vLLM / extractive model
                              |
                              v
                   answer + citations + trace
```

<p align="center">
  <img src="docs/assets/architecture.svg" alt="Enterprise GraphRAG supported runtime architecture" width="1100">
</p>

The important boundary is the tenant identity. A query does not receive a tenant ID from the browser or MCP tool arguments. The tenant comes from the verified access token and is passed into both retrieval backends.

## Requirements

The supported development runtime requires:

- Python 3.11 or newer
- a working C/C++ build environment only where the platform does not provide a pre-built dependency wheel
- optional Neo4j for a shared graph backend
- optional vLLM for model-backed generation and prompt-logprob scoring

The deterministic local path does not require a GPU, Neo4j server or external model API.

## Quick start

Clone the repository and enter it:

```bash
git clone https://github.com/SpryzenHell/enterprise_graphrag.git
cd enterprise_graphrag
```

Create a Python environment. A normal virtual environment is sufficient for the local runtime:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, use:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the application and test dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-enterprise.txt
```

Copy the example environment file:

```bash
cp .env.enterprise.example .env
```

For the local deterministic demo, leave the Neo4j and vLLM settings empty. Set a local development JWT secret in `.env` if you are not using the example secret.

Build the checked-in demo corpus:

```bash
python scripts/build_demo_index.py
```

Start the API:

```bash
python -m enterprise_graphrag.run --host 127.0.0.1 --port 8000
```

The browser UI is available at:

```
http://127.0.0.1:8000/
```

Create a development token in a second terminal:

```bash
source .venv/bin/activate
python -m enterprise_graphrag.token \
  --subject demo-user \
  --tenant acme \
  --scope graphrag:query
```

Paste that token into the browser UI and run:

```
How long does Acme retain incident records?
```

The checked-in Acme policy states that the retention period is 365 days.

## Conda and Jupyter

Conda can be used instead of `venv`:

```bash
conda create -n enterprise_graphrag python=3.11 -y
conda activate enterprise_graphrag
python -m pip install --upgrade pip
python -m pip install -r requirements-enterprise.txt
```

Jupyter is optional. If Jupyter is managed from a separate Conda environment, install `nb_conda_kernels` there and install `ipykernel` in `enterprise_graphrag`. The application itself does not depend on Jupyter.



## Default configuration

The example environment file contains the following deterministic defaults:

| Setting | Default |
| --- | --- |
| `GRAGRAPH_ENV` | `development` |
| `GRAGRAPH_JWT_MODE` | `shared_secret` |
| `GRAGRAPH_JWT_ALGORITHM` | `HS256` |
| `EMBEDDING_DIMENSION` | `384` |
| `TOP_K` | `8` |
| `VECTOR_WEIGHT` | `0.55` |
| `GRAPH_WEIGHT` | `0.45` |
| `RRF_K` | `60` |
| `SECURITY_PPL_THRESHOLD` | `80` |
| `SECURITY_MARKER_THRESHOLD` | `2` |
| `VLLM_MAX_CONTEXT_CHARS` | `32000` |
| `VLLM_MAX_DOCUMENT_CHARS` | `6000` |

Change these values through environment variables rather than editing application source files.

## API

Health:

```bash
curl http://127.0.0.1:8000/health
```

Readiness:

```bash
curl http://127.0.0.1:8000/ready
```

Tenant context:

```bash
curl \
  -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/v1/tenant
```

Query:

```bash
curl \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"How long does Acme retain incident records?"}' \
  http://127.0.0.1:8000/v1/query
```

The query response contains the answer, citations, a security decision, a retrieval trace and a graph trace.

The API also returns an `X-Request-ID` response header. The same identifier is included in the query trace.

## Browser application

The web application is intentionally small. It is served directly by FastAPI and does not require a second frontend build.

The figure is a static rendering of the supported browser UI using values from the checked-in deterministic corpus. It is documentation material, not a live production screenshot.

<p align="center">
  <img src="docs/assets/application-query.svg" alt="Enterprise GraphRAG browser application with an Acme query" width="1100">
</p>

The following figure represents a valid application state for a direct prompt-injection request. The text, blocked response and trace fields are taken directly from the supported security path.

<p align="center">
  <img src="docs/assets/application-blocked.svg" alt="Enterprise GraphRAG browser application showing a blocked prompt-injection request" width="1100">
</p>

## Retrieval and ranking

The runtime performs two tenant-scoped retrieval operations:

1. FAISS HNSW vector search.
2. Graph retrieval using either the in-memory graph or Neo4j.

The two rankings are combined with weighted Reciprocal Rank Fusion. The default weights are:

| Source | Weight |
| --- | ---: |
| Vector | 0.55 |
| Graph | 0.45 |

The values are configuration parameters and can be changed through `VECTOR_WEIGHT` and `GRAPH_WEIGHT`.

The FAISS index is physically partitioned by tenant. The tenant identifier is hashed before it is used in the filename. Tenant replacement is treated as an upsert; when an existing document is replaced, the tenant's HNSW index is rebuilt so stale vectors are not retained.

## Security boundary

The request is screened before retrieval. Retrieved titles and text are screened again before answer generation.

The gateway:

- normalizes Unicode compatibility characters;
- removes zero-width formatting characters;
- detects common instruction-override and data-exfiltration markers;
- blocks direct malicious queries;
- blocks retrieved documents when the marker threshold is exceeded;
- can add a vLLM prompt-logprob perplexity signal when a vLLM completion endpoint is configured.

The prompt-logprob signal is defense in depth. It is not presented as a general proof that prompt injection is impossible.

The deterministic security fixture includes separate Acme and Globex records plus an intentionally malicious imported memo.

<p align="center">
  <img src="docs/assets/security-evaluation.svg" alt="Deterministic security evaluation checks" width="1000">
</p>

## Evidence graph

The local memory graph used by the deterministic demo extracts single-token entities from document text. The following figure shows the corresponding Acme policy graph.

<p align="center">
  <img src="docs/assets/graph-trace.svg" alt="Tenant-scoped Acme evidence graph" width="950">
</p>

The Neo4j adapter uses a richer multi-word entity pattern, but the same tenant boundary and document-to-entity relationship are preserved.

## Tenant isolation

Every data-bearing request requires:

- a valid JWT;
- `sub`;
- `tenant_id`;
- `iss`;
- `aud`;
- `exp`;
- the `graphrag:query` scope.

The same tenant identity is used by the FastAPI query path and the MCP tool path.

<p align="center">
  <img src="docs/assets/tenant-isolation.svg" alt="Tenant isolation through JWT, FAISS and Neo4j" width="1050">
</p>

The Neo4j adapter uses explicit tenant predicates on document/entity lookup and trace operations. The FAISS backend uses one index per tenant.

Cross-tenant regression tests are part of the standard test suite.

## MCP

The supported MCP endpoint is:

```
http://127.0.0.1:8000/mcp/
```

The MCP server uses Streamable HTTP and bearer-token verification. The `hybrid_search` tool does not accept a tenant ID. Tenant identity is taken from the verified access token.

The server exposes:

- resource: `graphrag://capabilities`
- prompt: `grounded_query`
- tool: `hybrid_search`

<p align="center">
  <img src="docs/assets/mcp-flow.svg" alt="MCP authentication and GraphRAG request flow" width="1100">
</p>

The reusable MCP probe is:

```bash
python scripts/mcp_probe.py \
  --url http://127.0.0.1:8000/mcp/ \
  --token "$TOKEN" \
  --tenant acme \
  --query "incident records" \
  --expected-doc-id acme-retention
```

## Ingestion

For the small checked-in fixture:

```bash
python scripts/build_demo_index.py
```

For a real JSONL corpus:

```bash
python scripts/index_corpus.py \
  --corpus ./enterprise_data/corpus.jsonl \
  --batch-size 64
```

Selected tenants can be indexed explicitly:

```bash
python scripts/index_corpus.py \
  --tenant acme \
  --tenant globex
```

Each input record must contain:

```json
{
  "tenant_id": "acme",
  "doc_id": "acme-retention",
  "title": "Acme Incident Response Policy",
  "text": "Acme retains incident-response records for 365 days."
}
```

`doc_id` is the tenant-local primary key. Replaying the same document ID updates the existing record instead of creating a second retrieval record.

## Neo4j

For local development with the included Compose deployment:

```bash
export GRAGRAPH_ENV=development
export GRAGRAPH_JWT_SECRET='replace-with-a-long-random-secret'
export NEO4J_PASSWORD='testpassword'

docker compose -f docker-compose.enterprise.yml up -d
```

The application waits on Neo4j health before starting.

The Neo4j adapter:

- selects the configured database explicitly;
- uses parameterized Cypher;
- enforces composite uniqueness for tenant/document and tenant/entity identities;
- carries the tenant predicate through search and trace operations.

For a production deployment, use a managed or separately operated Neo4j service and supply its connection settings through the environment.

## vLLM

vLLM is optional for the deterministic local path.

When configured, the runtime uses:

- `/v1/chat/completions` for answer generation;
- `/v1/completions` for the prompt-logprob security signal;
- `/v1/embeddings` through the OpenAI-compatible embedding adapter when a separate embedding service is supplied.

Example:

```text
VLLM_BASE_URL=http://127.0.0.1:8001
VLLM_API_KEY=<provider-key-or-empty-for-local>
VLLM_MODEL=<model-id>
```

Keep vLLM private on an HPC node whenever possible. The repository documentation includes a private DGX layout and SSH forwarding example in [docs/HPC_VLLM.md](docs/HPC_VLLM.md).

A real provider check can be run with:

```bash
python scripts/provider_probe.py \
  --base-url "$VLLM_BASE_URL" \
  --api-key "$VLLM_API_KEY" \
  --chat-model "$VLLM_MODEL" \
  --embedding-model "$EMBEDDING_MODEL" \
  --embedding-dimension "$EMBEDDING_DIMENSION"
```

For a local vLLM server with no key, omit `--api-key`.

## Enterprise JWT / JWKS

Shared-secret JWT mode is intended for development and deterministic CI. Production should use an enterprise identity provider with asymmetric signing and JWKS.

Set:

```text
GRAGRAPH_ENV=production
GRAGRAPH_JWT_MODE=jwks
GRAGRAPH_JWT_ALGORITHM=RS256
GRAGRAPH_JWT_ISSUER=https://<issuer>
GRAGRAPH_JWT_AUDIENCE=<audience>
GRAGRAPH_JWT_JWKS_URL=https://<issuer>/.well-known/jwks.json
```

In production, the configuration validator rejects:

- the default or short shared secret;
- local/loopback issuer URLs;
- local/loopback JWKS URLs;
- wildcard MCP hosts/origins;
- loopback MCP hosts/origins;
- wildcard/loopback browser CORS origins.

The development token command is disabled in JWKS mode and must not be used as a production identity mechanism.

## Docker

Build the production image:

```bash
docker build -f Dockerfile.enterprise -t enterprise-graphrag:local .
```

The image runs as UID 10001 rather than root.

Run the standalone image:

```bash
docker run --rm \
  -p 8000:8000 \
  -e GRAGRAPH_ENV=development \
  -e GRAGRAPH_JWT_SECRET='replace-with-a-long-random-secret' \
  enterprise-graphrag:local
```

For the application plus Neo4j:

```bash
GRAGRAPH_ENV=development \
GRAGRAPH_JWT_SECRET='replace-with-a-long-random-secret' \
NEO4J_PASSWORD='testpassword' \
docker compose -f docker-compose.enterprise.yml up -d
```

The production deployment still requires real identity-provider, inference and data-store settings. The included Compose file is intended for repeatable deployment smoke testing, not as a complete internet-facing production topology.

## Tests

Run the normal test suite:

```bash
pytest -q enterprise_graphrag/tests
```

Run only the deterministic suite:

```bash
pytest -q enterprise_graphrag/tests -m "not integration and not gpu"
```

Run the Neo4j integration test when a Neo4j instance is available:

```bash
pytest -q enterprise_graphrag/tests/test_neo4j_integration.py -m integration
```

Run the deterministic security evaluation:

```bash
python scripts/evaluate_enterprise.py
```

Run the retrieval benchmark:

```bash
python scripts/benchmark_retrieval.py
```

The checked-in benchmark contains four labeled questions: two for Acme and two for Globex.

<p align="center">
  <img src="docs/assets/benchmark.svg" alt="Retrieval benchmark for the checked-in four-question fixture" width="900">
</p>

The current four-question fixture produces Recall@5 = 1.0 and MRR = 1.0 for vector, graph and hybrid retrieval. These values describe the checked-in fixture only. They are not production retrieval-quality claims.

## Runtime probes

The runtime probe checks:

- health;
- readiness;
- authenticated tenant context;
- authenticated query response;
- expected citation, when supplied;
- cross-tenant citation leakage.

Example:

```bash
python scripts/runtime_probe.py \
  --base-url http://127.0.0.1:8000 \
  --token "$TOKEN" \
  --tenant acme \
  --query "incident records" \
  --expected-doc-id acme-retention
```

The MCP probe performs an equivalent protocol-level check against the Streamable HTTP endpoint.

## GPU / A100 validation

The repository includes a separate self-hosted GPU workflow at [.github/workflows/gpu-validation.yml](.github/workflows/gpu-validation.yml).

It is designed for a long-lived private HPC allocation where the operator manages the Slurm allocation and keeps the GitHub runner online.

The runner uses:

```text
self-hosted
linux
x64
gpu-a100
```

The workflow validates actual hardware and inference behavior rather than only checking that packages are installed.

Before using the runner, read [docs/HPC_VLLM.md](docs/HPC_VLLM.md). In the current HPC environment, network access must be bootstrapped with:

```bash
python -c "import core_config"
```

That command must run before network-dependent commands in the runner's parent shell/process.

Do not put VPN credentials, SSH private keys, provider secrets or bearer tokens into the repository. Provider credentials for the GPU workflow belong in GitHub repository secrets.

## Validation path

The repository separates code-level regression checks from infrastructure-dependent validation.

<p align="center">
  <img src="docs/assets/validation-flow.svg" alt="Enterprise GraphRAG validation path" width="1100">
</p>

This makes it possible to run the deterministic suite from a fresh clone before configuring Neo4j or vLLM.

## Evidence and limitations

The repository deliberately separates repeatable local evidence from deployment-specific measurements.

The checked-in tests establish code-level invariants such as:

- tenant isolation;
- authentication and scope enforcement;
- FAISS storage integrity;
- Neo4j tenant predicates;
- injection filtering;
- MCP authentication;
- backend response validation.

The deterministic benchmark is a small fixture intended to make regressions visible. It is not representative of a production corpus.

Production latency, recall, throughput, GPU utilization, model quality, prompt-injection detection rate and end-to-end security performance should be measured on the actual deployment before being reported externally.

See [docs/VALIDATION.md](docs/VALIDATION.md) for the validation boundary and [SECURITY.md](SECURITY.md) for the security model.

## Repository layout

```text
enterprise_graphrag/
├── api.py                 FastAPI application
├── auth.py                JWT verification and demo tokens
├── config.py              environment and production validation
├── embeddings.py          hash + OpenAI-compatible embedding adapters
├── fusion.py              weighted RRF
├── llm.py                 extractive + vLLM answer models
├── mcp_server.py          MCP Streamable HTTP server
├── neo4j_store.py         tenant-aware Neo4j adapter
├── retrieval.py           hybrid retrieval + memory graph
├── security.py            retrieval security gateway
├── vector_faiss.py        tenant-partitioned FAISS HNSW
├── static/index.html      browser UI
└── tests/                 unit, contract, MCP, Neo4j and GPU tests

scripts/
├── build_demo_index.py
├── benchmark_retrieval.py
├── evaluate_enterprise.py
├── index_corpus.py
├── mcp_probe.py
├── provider_probe.py
├── runtime_probe.py
├── gpu_probe.py
└── start_hpc_runner.sh

docs/
├── DEMO.md
├── HPC_VLLM.md
└── VALIDATION.md
```

## References

- [Enterprise runtime documentation](enterprise_graphrag/README.md)
- [Demo guide](docs/DEMO.md)
- [Validation notes](docs/VALIDATION.md)
- [HPC / vLLM setup](docs/HPC_VLLM.md)
- [Security notes](SECURITY.md)
- [License](LICENSE)

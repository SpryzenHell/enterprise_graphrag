# Enterprise GraphRAG Agent — Production Runtime

This directory is the supported runtime for the merged project. The original GraphRAG-Local-UI, MCP CLI and ACE-derived trees remain for provenance; the supported application does not depend on the mechanically renamed legacy entrypoints.

## Architecture

FastAPI -> JWT tenant context -> FAISS HNSW + Neo4j graph retrieval -> weighted RRF -> retrieval security gateway -> vLLM/extractive answer -> citations + graph trace

### Implemented invariants

- Every data query requires a signed JWT containing tenant_id and the graphrag:query scope.
- FAISS uses one HNSW index per tenant and tenant IDs are hashed into filenames to prevent path collisions.
- Neo4j identities and traversals include the same tenant predicate.
- Vector and graph rankings are merged with weighted Reciprocal Rank Fusion.
- Retrieved content is screened before answer generation.
- When vLLM is configured, the security gateway can call /v1/completions with prompt_logprobs and calculate a perplexity signal.
- vLLM exposes OpenAI-compatible chat and embedding APIs used by the answer and embedding adapters. citeturn486974search1turn486974search4
- MCP uses the validated Python SDK 2.2.0 MCPServer surface, Streamable HTTP and first-class bearer token verification. The SDK supports a custom TokenVerifier plus AuthSettings for resource-server authentication. citeturn944949search0
- CI runs package compilation, deterministic tests, backend contract tests, a real Neo4j integration job and a labeled retrieval benchmark.

## Local validation

    python -m pip install -r requirements-enterprise.txt
    python -m compileall enterprise_graphrag scripts
    pytest -q enterprise_graphrag/tests
    python scripts/evaluate_enterprise.py
    python scripts/benchmark_retrieval.py

## Run the service

    python scripts/build_demo_index.py
    python -m enterprise_graphrag.run --host 127.0.0.1 --port 8000

Endpoints:

- GET /
- GET /health
- GET /docs
- POST /v1/query
- GET /v1/tenant
- POST /mcp/

Generate a development token:

    python -m enterprise_graphrag.token --subject demo-user --tenant acme --scope graphrag:query

The same bearer token is accepted by the FastAPI query endpoint and the MCP Streamable HTTP endpoint.

## Production backends

### Neo4j

Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD and NEO4J_DATABASE.

The adapter uses parameterized Cypher, explicit database selection and tenant-aware document/entity identity.

### vLLM

vLLM's OpenAI-compatible server provides the Completions, Chat Completions and Embeddings APIs. prompt_logprobs are supported on the Completions API and are used here only as one security signal. citeturn486974search1turn486974search4

### MCP

The current MCP Python SDK supports MCPServer, Streamable HTTP and a TokenVerifier/AuthSettings resource-server pattern. The configured verifier validates the same JWT used by the API and makes tenant_id available to the MCP tool layer. citeturn114184search0turn309280search3

For a deployed hostname, set MCP_RESOURCE_URL to the exact public MCP URL. The SDK's transport security should be configured with the real served host as part of production deployment. citeturn114184search4

## Evidence boundary

The checked-in deterministic tests verify architecture and security invariants. They are not evidence of production latency, retrieval quality, injection-detection rate or GPU throughput. Those numbers must be measured against the target corpus, model and deployment before entering a resume.


## Ingestion semantics

`doc_id` is the tenant-local primary key for ingestion.
Replaying a batch with an existing `doc_id` performs an upsert instead of creating duplicate retrieval records.
For FAISS HNSW, replacement documents trigger a rebuild of that tenant's index because HNSW vector deletion is not supported; append-only ingestion remains incremental.
Neo4j document upserts replace the document's `MENTIONS` relationships before creating the current entity links.
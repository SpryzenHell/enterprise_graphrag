# Enterprise GraphRAG Agent — Production Runtime

This directory is the supported runtime for the merged project. The original GraphRAG-Local-UI, MCP CLI and ACE-derived trees remain for provenance; the supported application does not depend on the mechanically renamed legacy entrypoints.

## Architecture

`FastAPI -> JWT tenant context -> FAISS HNSW + Neo4j graph retrieval -> weighted RRF -> retrieval security gateway -> vLLM/extractive answer -> citations + graph trace`

### Implemented invariants

- Every data query requires a signed JWT containing `tenant_id` and a `graphrag:query` scope.
- FAISS uses one HNSW index per tenant and tenant IDs are hashed into filenames to prevent path collisions.
- Neo4j identities and traversals include the same tenant predicate.
- Vector and graph rankings are merged with weighted Reciprocal Rank Fusion.
- Retrieved content is screened before answer generation.
- When vLLM is configured, the security gateway can call `/v1/completions` with `prompt_logprobs` and calculate a perplexity signal.
- vLLM exposes OpenAI-compatible chat and embedding APIs used by the answer/embedding adapters.
- MCP uses the current Python SDK `MCPServer` surface and Streamable HTTP.
- CI runs compile checks, tests and the deterministic evaluation.

## Local validation

```bash
python -m pip install -r requirements-enterprise.txt
python -m compileall enterprise_graphrag scripts
pytest -q enterprise_graphrag/tests
python scripts/evaluate_enterprise.py
```

## Run the service

```bash
python -m enterprise_graphrag.run --host 127.0.0.1 --port 8000
```

Endpoints:

- `GET /health`
- `GET /docs`
- `POST /v1/query`
- `GET /v1/tenant`
- `POST /mcp/`

Generate a development token:

```bash
python -m enterprise_graphrag.token --subject demo-user --tenant acme --scope graphrag:query
```

## Production backends

### Neo4j

Set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and `NEO4J_DATABASE`.

The adapter uses parameterized Cypher, explicit database selection and tenant-aware document/entity identity.

### vLLM

vLLM's OpenAI-compatible server provides `/v1/chat/completions`, `/v1/completions` and `/v1/embeddings`. The security layer uses prompt log-probabilities for its optional PPL signal.

### MCP

The current Python SDK's `MCPServer` provides tool/resource/prompt decorators and `streamable_http_app()`. When mounted in FastAPI, the host application's lifespan owns the MCP session manager.

## Evidence boundary

The checked-in deterministic tests verify architecture and security invariants. They are not evidence of production latency, retrieval quality, injection-detection rate or GPU throughput. Those numbers must be measured against the target corpus, model and deployment before entering a resume.

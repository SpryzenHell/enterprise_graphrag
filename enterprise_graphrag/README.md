# Enterprise GraphRAG Agent — Production Runtime

This directory is the supported runtime for the merged project. The original GraphRAG-Local-UI, MCP CLI and ACE-derived trees remain for provenance; the supported application does not depend on the mechanically renamed legacy entrypoints.

## Architecture

`FastAPI -> JWT tenant context -> FAISS HNSW + Neo4j graph retrieval -> weighted RRF -> retrieval security gateway -> vLLM/extractive answer -> citations + graph trace`

### Implemented invariants

- Every data query requires a signed JWT containing `tenant_id` and a `graphrag:query` scope.
- FAISS uses one HNSW index per tenant, so an ANN search cannot return another tenant's vectors.
- Neo4j identities and traversals include the same tenant predicate.
- Vector and graph rankings are merged with weighted Reciprocal Rank Fusion.
- Retrieved content is screened before answer generation.
- When vLLM is configured, the security gateway can call `/v1/completions` with `prompt_logprobs` and calculate a perplexity signal. vLLM also exposes OpenAI-compatible chat and embeddings endpoints. See the upstream docs before selecting a threshold.
- MCP is implemented with the current Python SDK's `MCPServer` and Streamable HTTP.
- CI runs compile checks and the isolated test suite.

## Local validation

```bash
python -m pip install -r requirements-enterprise.txt
python -m compileall enterprise_graphrag
pytest -q enterprise_graphrag/tests
```

## Run the service

```bash
python -m enterprise_graphrag.run --host 127.0.0.1 --port 8000
```

The service exposes:

- `GET /health`
- `GET /docs`
- `POST /v1/query`
- `GET /v1/tenant`
- `POST /mcp` (Streamable HTTP)

Generate a development token:

```bash
python -m enterprise_graphrag.token --subject demo-user --tenant acme --scope graphrag:query
```

## Production backends

### Neo4j
Set:

```text
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<secret>
NEO4J_DATABASE=neo4j
```

The adapter uses parameterized Cypher, explicit database selection and tenant-aware document/entity identity.

### vLLM
vLLM's current OpenAI-compatible server supports `/v1/chat/completions` and `/v1/embeddings`. The security layer uses `/v1/completions` with `prompt_logprobs` when PPL scoring is configured.

### MCP
The current Python SDK exposes `MCPServer`, tool/resource/prompt decorators, and `streamable_http_app()`. When mounted inside FastAPI, the host lifespan starts the MCP session manager.

## Evidence boundary

The code does not fabricate production metrics. Accuracy, latency, injection-detection rates, retrieval recall/MRR and GPU throughput must be measured against the actual corpus, model and deployment before being placed on a resume.

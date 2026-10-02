# Enterprise GraphRAG Agent — Production Runtime

This directory is the supported runtime for the merged project. The original GraphRAG-Local-UI, MCP CLI, and ACE-derived trees remain in the repository for provenance; this package avoids depending on mechanically renamed upstream entrypoints.

## Target architecture

`FastAPI -> JWT tenant context -> tenant-scoped vector + graph retrieval -> weighted RRF -> retrieval security gateway -> vLLM/extractive answer -> citations + graph trace`

### Resume claim mapping

1. **Row-Level Security:** every request has a signed JWT with `tenant_id`; retrieval must use that tenant. Production FAISS is partitioned per tenant and Neo4j queries require the same tenant predicate.
2. **FAISS + Neo4j rank fusion:** vector and graph rankings are merged with weighted Reciprocal Rank Fusion. Neo4j is an optional production adapter; local tests use an in-memory graph with the same tenant boundary.
3. **Indirect prompt injection:** retrieved evidence is screened before generation. When vLLM is configured, the gateway can request prompt log-probabilities and calculate a perplexity signal; marker rules provide a second signal and defense-in-depth.

## Important evidence boundary

The code implements the integrations, but no production latency/accuracy/security percentage should be claimed until the real Neo4j, FAISS corpus, embedding model and vLLM server have been run and benchmarked. The repository deliberately keeps those measurements reproducible instead of fabricating them.

## Development

From the repository root:

```bash
python -m pip install -r requirements-enterprise.txt
pytest -q enterprise_graphrag/tests
```

Production configuration is documented in `.env.enterprise.example`.

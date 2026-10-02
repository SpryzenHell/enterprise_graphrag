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

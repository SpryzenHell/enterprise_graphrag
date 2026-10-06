# Fixture experiments

The repository runs a reproducible experiment suite over the checked-in five-document corpus. The suite uses the same retrieval, graph, vector and security classes used by the application.

The suite is intentionally broad. It covers retrieval quality, retrieval depth, RRF weighting, vector/graph agreement, query variants, graph structure, tenant isolation, prompt-injection handling, persistence, document replacement and FAISS storage integrity.

## Dataset

| Measure | Acme | Globex | Total |
| --- | ---: | ---: | ---: |
| Documents | 3 | 2 | 5 |
| Text characters | 368 | 228 | 596 |
| Words (whitespace split) | 48 | 29 | 77 |

One Acme document is intentionally malicious so the retrieval security path can be tested.

<p align="center">
  <img src="assets/fixture-dataset-profile.svg" alt="Checked-in corpus profile" width="1000">
</p>

## Retrieval depth

The expected document is evaluated at K = 1, 2, 3, 4 and 5.

| Retriever | Recall | MRR | Mean rank |
| --- | ---: | ---: | ---: |
| Vector | 1.00 | 1.00 | 1.00 |
| Graph | 1.00 | 1.00 | 1.00 |
| Hybrid RRF | 1.00 | 1.00 | 1.00 |

All four labeled questions keep the expected document at rank 1 for all tested K values.

<p align="center">
  <img src="assets/retrieval-experiments.svg" alt="Retrieval depth experiment" width="1000">
</p>

## RRF weight sensitivity

The vector weight is swept from 0.0 to 1.0 in increments of 0.1. The graph weight is the complement.

Every tested weight keeps Recall@5 = 1.00 and MRR = 1.00 on this fixture.

<p align="center">
  <img src="assets/retrieval-heatmap.svg" alt="Retrieval stability heatmap" width="1050">
</p>

This result says the small fixture is stable under weighting changes. It does not identify a best production weighting.

## Vector / graph agreement

For every canonical question, the experiment records:

- vector top-5 IDs;
- graph top-5 IDs;
- set overlap / Jaccard score;
- which hybrid results were supported by vector, graph or both.

This is useful because good hybrid ranking should not be judged only by the final rank. The report also shows where the two retrievers agree and where one retriever supplies unique evidence.

## Query variants

Each canonical query is tested in several forms:

- original text;
- uppercase;
- lowercase;
- extra surrounding / repeated spaces;
- question-mark variant.

The report records vector, graph and hybrid expected-document rank for every variant. This is a stability experiment, not a claim that every arbitrary paraphrase will preserve retrieval quality.

## Graph structure

The graph experiment records, per tenant:

- document count;
- number of unique extracted entities;
- document-to-entity edge count;
- mean entities per document;
- maximum entities in one document.

The checked-in graph is intentionally small, but this view exposes how much of the evidence is coming through the graph path.

The graph profile in the current fixture report is computed from the same local memory graph used by the experiment suite. It records document counts, unique entities, document-to-entity edges, and entity counts per document.

## Tenant matrix

Every labeled question is run against every tenant.

For every combination, the report stores:

- question tenant;
- query tenant;
- returned document IDs;
- cross-tenant document IDs.

The test requires zero cross-tenant IDs in every row.

<p align="center">
  <img src="assets/security-matrix.svg" alt="Security and tenant test matrix" width="1050">
</p>

## Prompt-injection cases

The security suite covers:

1. a direct instruction override;
2. the malicious retrieved document;
3. a zero-width Unicode version of the instruction;
4. the normal authorized query path.

The experiment verifies that malicious retrieved content does not reach the allowed context set.

## Persistence and data changes

The experiment also checks the behavior that matters during real operation:

| Check | Expected result |
| --- | --- |
| FAISS restart | Stored tenant index can be loaded |
| Graph restart | Stored graph state can be loaded |
| Document replacement | New record replaces the old record |
| Incomplete FAISS storage | Read fails closed |
| Artifact files | Index, metadata and manifest exist and have non-zero size |

The experiment report also records the total size of the temporary FAISS artifacts created for the fixture.

## Security result

For the malicious `acme-injected` document:

- it can appear as a retrieval candidate;
- the security gateway rejects it;
- the rejected item does not enter the allowed context list;
- the answer model therefore does not receive that document.

For the four canonical tenant queries, cross-tenant leaks are zero.

## Reproduce

Run:

```bash
python scripts/analyze_fixture.py
```

The script writes:

```text
enterprise_data/fixture_experiments.json
```

Run the visual report checks with the normal test workflow. The repository includes detailed SVG views so the measured results can be inspected without opening the raw JSON.

## Interpretation

The five-document fixture is useful for regression testing and code-level behavior. It is not large enough to support production claims.

Do not use these values as production retrieval quality, production latency, throughput or security-rate measurements. For a real deployment, repeat the same experiment families on the target corpus, embedding model, answer model and security test set.

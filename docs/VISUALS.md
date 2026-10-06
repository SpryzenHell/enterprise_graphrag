# Visual guide

The repository does not use screenshot-style UI mockups or invented deployment screens. The checked-in visual assets are either architecture schematics or static plots whose values can be traced to the repository's fixture data, source configuration, or recorded CI evidence.

## Architecture schematics

- [architecture.svg](assets/architecture.svg) — supported request and answer flow.
- [data-lineage.svg](assets/data-lineage.svg) — checked-in ingestion, retrieval, fusion, security and answer path.
- [tenant-isolation.svg](assets/tenant-isolation.svg) — JWT-derived tenant boundary through vector and graph retrieval.
- [graph-trace.svg](assets/graph-trace.svg) — example graph trace from the checked-in Acme corpus.
- [mcp-flow.svg](assets/mcp-flow.svg) — MCP request flow with token-derived tenant identity.
- [security-evaluation.svg](assets/security-evaluation.svg) — deterministic security evaluation result.
- [validation-flow.svg](assets/validation-flow.svg) — the current repository validation path.

## Fixture plots

- [benchmark.svg](assets/benchmark.svg) — Recall@5 and MRR for the four labeled fixture questions.
- [fixture-dataset-profile.svg](assets/fixture-dataset-profile.svg) — document, word and character counts derived from `enterprise_data/corpus.jsonl`.
- [retrieval-experiments.svg](assets/retrieval-experiments.svg) — retrieval-depth results for K=1..5.
- [rrf-weight-sensitivity.svg](assets/rrf-weight-sensitivity.svg) — vector/graph RRF weight sweep from 0.0 to 1.0.
- [retrieval-heatmap.svg](assets/retrieval-heatmap.svg) — the K × vector-weight fixture result matrix.
- [security-matrix.svg](assets/security-matrix.svg) — deterministic security and tenant-isolation cases.

## Accuracy checks

`scripts/check_visual_facts.py` is run by CI after the fixture experiment report is generated. It cross-checks the plotted values against `enterprise_data/fixture_experiments.json` and rejects the build when a visual drifts from the checked-in measurements.

The visuals are not presented as screenshots of an unverified production deployment. The real browser UI remains the checked-in `enterprise_graphrag/static/index.html`.

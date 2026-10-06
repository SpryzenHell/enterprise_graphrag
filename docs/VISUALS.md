# Visual guide

The repository uses several visual styles because each one answers a different question.

## 1. Browser workbench

[workbench-ui.svg](assets/workbench-ui.svg)

A UI-style view of the actual application concept. It shows:

- question input and top-K control;
- grounded answer;
- graph view;
- retrieved-source table;
- security decision;
- execution trace;
- raw JSON response.

The real browser UI in `enterprise_graphrag/static/index.html` exposes the same logical tabs and builds the graph view from the API response.

## 2. Graph explorer

[graph-rag-explorer.svg](assets/graph-rag-explorer.svg)

A graph-first view for understanding how documents connect to extracted entities and how those results feed the evidence list.

## 3. Data lineage

[data-lineage.svg](assets/data-lineage.svg)

A left-to-right pipeline showing the complete path:

`JSONL → validation → vector + graph paths → search → RRF → security → answer`.

This is useful when checking where tenant and security controls are applied.

## 4. Experiment command center

[experiment-command-center.svg](assets/experiment-command-center.svg)

A dashboard-style view covering:

- dataset profile;
- retrieval depth;
- RRF weight sensitivity;
- security cases;
- storage/update checks;
- query variants.

## 5. Retrieval heatmap

[retrieval-heatmap.svg](assets/retrieval-heatmap.svg)

A matrix-style plot for K and vector weight. On this fixture, every tested combination keeps the expected document at rank 1.

## 6. Security matrix

[security-matrix.svg](assets/security-matrix.svg)

A test-matrix style view covering direct instruction override, retrieved injection, Unicode obfuscation, tenant isolation and a normal authorized query.

## 7. CI terminal snapshot

[ci-validation-main.svg](assets/ci-validation-main.svg)

A high-contrast terminal-style snapshot of the successful default-branch CI run.

## Accuracy rule

The visuals in this repository are tied to checked-in fixture values or recorded CI results. They are not presented as screenshots from an unverified production deployment.

When the fixture data changes, regenerate or update the related visual before treating the numbers as current.

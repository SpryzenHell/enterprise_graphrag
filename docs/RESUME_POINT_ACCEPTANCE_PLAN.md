# Resume-point acceptance plan: Enterprise GraphRAG

Last updated: 2026-10-16

This plan distinguishes implemented architecture from evidence that the claim works on an external benchmark. A résumé point is not marked complete solely because a unit test passes or the code path exists.

## 1. Strict row-level security via MCP and JWT-derived tenant identity

### Required evidence
- Authenticated REST query and MCP tool calls derive the tenant from the verified JWT principal, never from a request-body `tenant_id`.
- Attempts to query another tenant, inject another `tenant_id` in a body/tool argument, trace a foreign document, or replace a same-ID document cannot return foreign-tenant content.
- The same invariants are checked against the in-memory test backend and live Neo4j integration backend.

### Acceptance gate
- Zero cross-tenant citations/traces in all adversarial regression cases.
- Invalid/missing JWTs are rejected; body/tool-argument tenant spoofing does not alter the principal.
- Neo4j integration tests and standard CI must pass.

### Existing evidence
- `enterprise_graphrag/tests/test_core.py`: request-body tenant spoofing test.
- `enterprise_graphrag/tests/test_mcp_http.py`: authenticated MCP tenant test and cross-tenant MCP query test.
- `enterprise_graphrag/tests/test_neo4j_integration.py`: live Neo4j tenant isolation, bulk upsert, stale-link removal, and two-hop tenant-scoped retrieval.
- The Enterprise GraphRAG CI at SHA `b67fa4af6d752b5e317ab56828fc7b9eb0b7e... ` passed unit, container smoke, compose smoke, and Neo4j integration jobs on 2026-10-16. Use the exact workflow run as the source of record: https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38884930814

### Remaining qualification
This establishes reproducible implementation and integration-test evidence, not a third-party security audit or proof of absence of every possible side channel.

## 2. FAISS + Neo4j retrieval and rank fusion for supporting evidence

### Evaluation datasets and licenses
- BEIR SciFact corpus and official test qrels: CC-BY-SA-4.0.
- HotpotQA distractor validation supporting facts: CC-BY-SA-4.0.
- `sentence-transformers/all-MiniLM-L6-v2`: Apache-2.0.
- `BAAI/bge-base-en-v1.5`: MIT.

### Measured baseline
On a fixed-seed 150-query SciFact sample:
- MiniLM FAISS vector-only: Recall@10 0.7733, MRR@10 0.6011, nDCG@10 0.6391.
- BGE FAISS vector-only: Recall@10 0.8640, MRR@10 0.7076, nDCG@10 0.7425.
- BGE + current Neo4j RRF: Recall@10 0.8640, MRR@10 0.6624, nDCG@10 0.7121.

On an earlier 400-query HotpotQA sample:
- Vector-only: supporting-title Recall@10 0.9450, MRR@10 0.9433, nDCG@10 0.8895.
- A first RRF configuration: recall gain +0.0025, MRR delta -0.0810, nDCG delta -0.0726. **This configuration failed the acceptance gate and must not be promoted.**
- Neo4j vector-seeded two-hop expansion added a few supporting candidates to the top-100 pool; candidate generation/ranking remains the open problem.

### Predeclared gate for any retrieval promotion
- At least +0.01 absolute supporting-title Recall@10 on untouched held-out queries.
- MRR@10 and nDCG@10 regression no worse than -0.02 relative to BGE vector-only.
- Selection/tuning uses only the calibration half. Final metrics come from a frozen configuration on the held-out half.
- If no configuration passes, vector-only BGE remains the default; report the graph/fusion path as implemented but not yet proven to improve quality.

### Current experiments
- Independent vector/graph candidate-depth sweep: https://github.com/SpryzenHell/enterprise_graphrag/pull/10
- Vector-prefix-protected RRF tail augmentation: https://github.com/SpryzenHell/enterprise_graphrag/pull/11
- Live Neo4j integration is run before the expensive multi-hop benchmark. The benchmark evaluates supporting-title recall, hit@10, all-supports@10, MRR, nDCG, exact answer-string coverage, and query latency.

## 3. Indirect prompt-injection filtering with real-time PPL at the API gateway

### Failed baselines that must remain visible
The original marker-only gate blocked 0/200 injected examples in an initial balanced synthetic sample. A small semantic classifier later achieved high synthetic TPR but generalized poorly:
- Horizon small on an external fixed-seed sample: synthetic-v2 TPR 0.82/FPR 0.02; BIPIA TPR 0.01/FPR 0; PIArena TPR 0.07/FPR 0; NotInject benign FPR 0.20; OR-Bench-hard benign FPR 0.11.
- A ProtectAI DeBERTa baseline caught more BIPIA attacks but had a 0.20 BIPIA benign FPR in the tested sample.
These results do **not** substantiate the résumé point on their own. Do not enable those detectors as the default gate based only on synthetic-set performance.

### Datasets/models and licensing
- `Horizon-Labs/prompt-injection-eval-suite`: per-config licenses are recorded by the benchmark script; `synthetic_v2_test` Apache-2.0, `bipia` CC-BY-SA-4.0, `piarena` MIT, `notinject` MIT, `orbench_hard` CC-BY-4.0.
- `neuralchemy/Prompt-injection-dataset` training config: Apache-2.0 dataset card; preserve group identifiers and remove evaluation-text overlap.
- `geodesic-research/bipia/bipia`: CC-BY-SA-4.0; preserve attribution and review share-alike implications before redistributing derivative weights.
- `bench-llm/or-bench` training split: CC-BY-4.0; keep evaluation text excluded from training.
- Base `Horizon-Labs/prompt-injection-guard-base`: Apache-2.0 per model card.
- Real PPL model `Qwen/Qwen2.5-0.5B-Instruct`: Apache-2.0.

### Current training/evaluation path
Workflow: https://github.com/SpryzenHell/integrator/blob/graphrag-notinject-hard-negative-guard-2026-10-15/.github/workflows/graphrag-notinject-hard-negative-guard.yml

- Mixed-corpus training with BIPIA, a separate prompt-injection training corpus, OR-Bench hard negatives, and hash-partitioned NotInject examples.
- Duplicate/context groups and exact evaluation text are excluded across training/calibration/holdout boundaries.
- The validation JSONL writer now uses literal LF record delimiters and JSON round-trip checks; this fixes a previous false failure where `str.splitlines()` counted valid Unicode separators inside text as extra records.
- The A100 job checks CUDA/A100 availability, runs API/RLS/MCP/split-integrity tests, fine-tunes the guard, starts vLLM, calibrates a combined semantic+PPL operating point on disjoint validation, then compares base vs fine-tuned model with the same frozen thresholds on the holdout.

### Promotion gate
- Joint semantic/PPL validation must have a feasible operating point.
- Candidate must improve BIPIA TPR by at least +0.10 absolute versus the frozen-threshold base model while candidate BIPIA FPR stays at or below 0.05.
- PIArena candidate TPR must be within 0.03 of base and PIArena FPR must be at or below 0.02.
- Synthetic direct/v2/docs TPR regression tolerance: 0.03; FPR must be no more than min(0.05, base FPR + 0.02).
- NotInject and OR-Bench-hard benign FPR must each be at or below 0.05.
- The integrated PPL thresholds must come from validation, never from the holdout.
- If no feasible calibration exists, diagnostic reports should still be collected where possible, but `compare_guard_reports.py` must reject promotion. If any acceptance condition fails, keep the current model and iterate.

### Current execution state at last update
- Latest A100 run: https://github.com/SpryzenHell/integrator/actions/runs/38884998907
- CPU preflight is green. The job has verified the A100 hardware and passed API/RLS/MCP/split-integrity regressions; fine-tuning is in progress.
- PPL calibration and base-vs-candidate holdout results have not completed yet. The injection-defense résumé point is therefore **not yet verified**.

## 4. Report format for every new version

Every candidate version should produce a machine-readable JSON, a readable Markdown summary, source commit SHA, dataset/model/license references, sampling seed, sample counts per source and class, TPR/FPR/F1/ROC-AUC by config, p50/p95 inference latency, PPL score coverage/latency, retrieval metrics, and the exact acceptance decision.

Do not select thresholds on the final holdout; do not train on evaluation text; do not label a point “achieved” unless its predeclared gate passes. A candidate that fails is still useful diagnostic evidence, but is not a production promotion.

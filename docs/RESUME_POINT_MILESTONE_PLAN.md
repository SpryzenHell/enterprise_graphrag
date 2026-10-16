# Resume-point engineering milestone plan

Status date: 2026-10-16

This document defines what must be measured before the three Enterprise GraphRAG resume claims should be treated as substantiated. A green unit-test suite, the existence of a workflow, or a fixture-only demonstration is not enough on its own. Results must be tied to a source commit, fixed dataset/sample, model ID, settings, and saved report.

## Milestone A — Strict tenant isolation through API and MCP

**Resume claim:** Enforced strict Row-Level Security by architecting an Agentic GraphRAG via the Model Context Protocol.

Acceptance criteria:

1. API and MCP request identity is derived from the validated authentication token; user-provided request fields must not override the authorized tenant.
2. FAISS indexes and graph queries are tenant-scoped. Neo4j traversal predicates must constrain the tenant on anchors, bridge entities, and returned documents.
3. RRF keys on `(tenant_id, doc_id)`, not document ID alone.
4. Test with identically named entities and colliding document IDs in at least two tenants. No cross-tenant hit, citation, trace node, or MCP result is permitted.
5. Verify token spoof attempts, missing tenant claims, stale graph edges after upserts, and the live API/MCP routes. Run the unit, Neo4j integration, and Compose/container tests.

Pass gate: **zero cross-tenant citations and trace nodes across the complete regression suite**; all authenticated API/MCP tenant-spoof tests pass.

Current evidence: the regular CI suite and live Neo4j integration suite passed on commit `774e5fde22b4bd08638cde3e5b1673551e7427a6`, including bulk upsert, stale-entity removal, and tenant-scoped vector-seeded traversal. The Compose smoke test also passed. Keep the live external API/MCP run as a separate evidence item.

## Milestone B — Hybrid retrieval and Rank Fusion

**Resume claim:** Mitigated LLM hallucinations by merging FAISS vector embeddings with Neo4j traversals via Rank Fusion.

Datasets and models:

- BEIR SciFact test qrels, CC BY-SA 4.0.
- HotpotQA distractor validation supporting facts, CC BY-SA 4.0.
- `BAAI/bge-base-en-v1.5` embedding model, MIT.

Required experiments:

1. Always publish vector-only and Neo4j-only controls.
2. Evaluate direct Neo4j full-text, vector-seeded two-hop expansion, rarity-aware expansion, and weighted RRF across fixed candidate depths and weights.
3. Split sampled queries deterministically into calibration and held-out groups. Choose settings only on calibration; report the frozen choice on held-out queries.
4. Report supporting-title Recall@10, hit@10, all-supporting-titles@10, MRR@10, nDCG@10, answer-string coverage, index/ingest time, and p50/p95 query latency.
5. Preserve the full sweep table and chosen hyperparameters. Do not describe evidence retrieval as a complete end-to-end hallucination test; that requires separate answer correctness/faithfulness evaluation.

Retrieval pass gate for a genuine hybrid improvement: on the frozen held-out query subset, supporting-title Recall@10 improves by at least **1 percentage point** versus vector-only, while MRR@10 and nDCG@10 regress by no more than **0.02 absolute** each. The graph traversal and RRF route must also pass tenant-isolation tests. If no configuration passes, retain the vector-only configuration as the default and report the best hybrid as experimental.

Current evidence:

- On 150 SciFact queries, BGE vector-only measured Recall@10 **0.8640**, MRR@10 **0.7076**, nDCG@10 **0.7425**; the earlier MiniLM vector baseline measured **0.7733 / 0.6011 / 0.6391**. BGE improved retrieval quality materially, but the earlier graph-RRF run retained recall while lowering MRR/nDCG.
- On the 120-query HotpotQA pilot, vector-only held-out supporting-title Recall@10 was **0.975**, MRR@10 **0.923611**, and nDCG@10 **0.896231**. The tuned hybrid held the same recall with MRR lower by **0.019444** and nDCG lower by **0.015168**; it failed the declared retrieval gate because recall did not improve.
- A rarity-aware vector-seeded Neo4j experiment is now under evaluation on a new HotpotQA run. The case-normalized entity-hub regression and standard CI pass on commit `774e5fde22b4bd08638cde3e5b1673551e7427a`; the 400-query result is not yet recorded here because its benchmark step is still running.

## Milestone C — Indirect prompt-injection defense with real-time perplexity

**Resume claim:** Blocked indirect prompt injections by deploying real-time Perplexity evaluation filters at the API gateway.

Datasets/models used in the experimental matrix:

- BIPIA (CC BY-SA 4.0).
- PIArena (MIT).
- NotInject (MIT).
- OR-Bench hard negatives / OR-Bench-80K (CC BY 4.0).
- Synthetic prompt-injection configurations only where their dataset card specifies an applicable license.
- `Horizon-Labs/prompt-injection-guard-base` (Apache-2.0 per model card) and `Qwen/Qwen2.5-0.5B-Instruct` (Apache-2.0) for the actual vLLM prompt-logprob evaluation.

Required experiments:

1. Score the existing semantic gate and the combined semantic + real vLLM perplexity gate on identical, fixed samples.
2. Use independent validation/calibration partitions and hash-deduplicate training rows from held-out data. Test long documents, start/middle/end attacks, markerless attacks, Unicode-obfuscated attacks, malformed/absent logprobs, and benign hard negatives.
3. Measure true-positive rate (TPR), false-positive rate (FPR), precision, F1, per-dataset confusion matrices, PPL call coverage, inference throughput, and p50/p95 latency.
4. Select thresholds only on calibration partitions. Do not promote a checkpoint or threshold if no feasible threshold meets the false-positive limits.
5. Verify the API gateway uses the same production scoring path as the evaluation; exercise a real vLLM service with token-logprob requests and the live query route.
6. Keep dataset/model licenses and training-data overlap notes attached to every checkpoint. Do not claim broad indirect-injection coverage from synthetic-only metrics.

Promotion gates for the mixed-corpus candidate:

- Validation FPR at most **5%** on overall benign, NotInject, and OR-Bench-80K; PIArena validation FPR at most **2%**.
- On untouched OOD samples, NotInject and OR-Bench-hard FPR at most **5%**; PIArena FPR at most **5%**.
- Improve BIPIA TPR by at least **10 percentage points** versus the frozen baseline without a PIArena TPR regression of more than **3 percentage points** or a synthetic TPR regression greater than **3 percentage points**.
- Run the full set with real vLLM perplexity enabled. The candidate must pass threshold calibration before promotion.

Current evidence: the earlier semantic-only models generalized poorly to BIPIA and PIArena. An A100-run mixed-corpus candidate improved BIPIA TPR by 45 points but was **rejected**: measured FPR was 27% on `synthetic_direct_test`, 22% on NotInject, and 9% on PIArena, exceeding the acceptance limits. The disjoint-data retraining/acceptance workflow on the `a4-test` A100 runner has not started at the last status check (GitHub Actions still reports the run as pending with no job), so there is no accepted new model to claim yet. Keep the prior model active until a candidate passes.

## Milestone D — End-to-end evidence and release discipline

A release candidate must include a single report bundle linking:

- source commit and workflow run URLs;
- deterministic unit tests plus real Neo4j integration;
- authenticated API and MCP tenant-boundary evidence;
- vector-only vs. hybrid retrieval metrics and the complete calibration/held-out split;
- semantic-only vs. real-PPL combined gate metrics;
- dataset/model licensing and cache/checkpoint identifiers;
- an explicit `PASS`, `FAIL`, or `NOT RUN` for each resume point.

Promotion is gated on all three milestones. A partially successful branch, fixture-only test, or pending A100 run is not a completed project milestone.

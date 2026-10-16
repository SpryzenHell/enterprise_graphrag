# GraphRAG Milestone Experiment Log — 2026-10-14

This log records measurements emitted by GitHub Actions. A successful smoke test is not treated as proof of a quality target, and synthetic fixture results are not presented as production results.

## A100 runtime and live API

Workflow: [A100 security/retrieval evaluation #38586061884](https://github.com/SpryzenHell/integrator/actions/runs/38586061884)

- Hardware assertion: passed on the self-hosted A100 runner; CUDA PyTorch and vLLM dependencies installed.
- Qwen vLLM startup and /v1/models readiness: passed.
- Deterministic GraphRAG tests: **78 passed, 6 deselected**.
- Live API runtime probe: health and readiness passed; authenticated query returned 2 citations; observed end-to-end query latency was about 5.8 s on this run.
- Live API tenant/injection smoke: HTTP 200; 2 citations; no_cross_tenant_citations=true; markerless_injection_blocked=true; markerless_injection_not_cited=true.
- MCP HTTP probe: initialized successfully, discovered hybrid_search, and returned 2 Acme-scoped citations.
- Overall workflow: **failed** because test_vllm_prompt_logprobs_contract expected prompt_token_ids, which this vLLM response did not include. The server returned prompt_logprobs, but the optional token-ID field was absent. This is a real failed contract, not a passed PPL test.

The code was updated to request the OpenAI-compatible echoed-token logprobs form as well, accept either correctly aligned vLLM prompt_logprobs plus token IDs or the observed-token logprobs.token_logprobs fallback, and treat malformed responses as unscorable. New CPU regression tests passed in [CI run #38591251926](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38591251926). The A100 rerun is queued at [#38589065787](https://github.com/SpryzenHell/integrator/actions/runs/38589065787), to verify the fallback against a real vLLM response.

## A100 BGE vector retrieval

Evidence artifact from the same A100 workflow, artifacts/graphrag-real-evaluation/real_evaluation.json:

- Corpus: 5,183 SciFact documents.
- Queries: 150 official test-qrels-backed queries.
- Device: CUDA; BGE index build: **30.954 s** on the A100 run.
- Dataset: BEIR SciFact, CC-BY-SA-4.0.
- Embedding model: BAAI/bge-base-en-v1.5, MIT.

| Method | Recall@1 | Recall@5 | Recall@10 | MRR@10 | nDCG@10 |
|---|---:|---:|---:|---:|---:|
| BGE vector-only | 0.5919 | 0.8280 | 0.8640 | 0.7076 | 0.7425 |
| In-memory graph-only | 0.0833 | 0.2302 | 0.2969 | 0.1520 | 0.1843 |
| BGE + in-memory graph RRF (0.55/0.45) | 0.5102 | 0.8117 | 0.8640 | 0.6577 | 0.7072 |

Interpretation: BGE materially improves over the former MiniLM vector baseline, but the tested RRF setting **does not improve MRR/nDCG over BGE-only** on SciFact. This supports a stronger embedding baseline, not a claim that current fusion improves general ranking quality. The A100 run intentionally did not attach Neo4j; a separate live-Neo4j benchmark is running.

## Perplexity and injection evidence

- The real-evaluation report configured Qwen as the PPL source but recorded **0 observed PPL scores out of 400 sampled security examples**. Thus the PPL portion of that experiment contributed no measured scores.
- In the extra synthetic direct-injection sample, the semantic classifier alone scored TPR 0.56 / FPR 0.01, and the combined semantic/PPL policy scored TPR 0.68 / FPR 0.02. PPL coverage in that report was 0, so the combined value does not demonstrate a PPL improvement.
- On the synthetic v2 sample, semantic scores were stronger, but publisher-generated synthetic performance is not sufficient to establish general indirect-injection protection.
- Prior independent fixed-seed model comparisons still show poor generalization for the small off-the-shelf model (BIPIA and PIArena TPR only in the low single digits in the tested CPU samples).
- The first BIPIA-fine-tuned checkpoint is invalid for selection because an earlier data-construction bug supplied the cleaned text for both classes. It must not be used as proof or deployed.

Corrective work:
1. The PPL parser now supports the second observed-token response shape, validates malformed responses, and fails closed when an eligible second-stage PPL check is configured but cannot return a valid score. CPU CI passed after these changes.
2. The BIPIA pair builder now emits real clean negatives and real poisoned positives, removes repeated payload copies from negatives, and asserts this invariant. The pure-Python pair-builder tests and full-loader regression pass.
3. A corrected A100 fine-tune with external evaluation is running/queued in [workflow #38586063917](https://github.com/SpryzenHell/integrator/actions/runs/38586063917).
4. The PPL milestone remains **not achieved** until a fresh A100 run produces valid nonzero PPL score coverage and the frozen detector/policy hits the predeclared held-out recall/FPR bar on independent injection and benign-hard-negative samples.

## Tenant RLS evidence

- The A100 live API smoke reported no cross-tenant citations and blocked a markerless injected passage; the MCP probe returned only Acme-scoped citations.
- CPU CI on the corrected security branch passed standard tests, live Neo4j integration, container smoke and compose smoke.
- A negative MCP call now includes a body-supplied tenant_id="globex" while authenticated as Acme, to verify that arguments cannot override the JWT tenant.
- Treat this as strong regression evidence for the tested cases, not a proof over every possible tenant claim or backend error. Continue to require zero leaked IDs/citations from the complete adversarial test suite.

## Active independent retrieval benchmark

[Live Neo4j two-hop + BGE benchmark #38581864122](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38581864122) has passed dependency installation, syntax compilation, regression, and live Neo4j tenant-isolation tests. It is still working through the BGE vector / real Neo4j / RRF benchmark stage; no final artifact was available when this log was authored. Until its held-out metrics are available, the multi-hop fusion target remains open.

## Acceptance decision at log time

| Resume point | Evidence status | Decision |
|---|---|---|
| Strict RLS via MCP/agent | Adversarial API/MCP smoke and live Neo4j tests pass in covered scenarios | **Strong progress; continue full adversarial validation** |
| FAISS + Neo4j traversals + rank fusion reduces unsupported answers | BGE vector is strong; tested SciFact RRF is worse than vector-only ranking; live Neo4j/multi-hop holdout pending | **Not yet achieved** |
| Real-time PPL indirect-injection gate | A100 server starts, but old prompt-logprob contract failed and PPL score coverage was 0 in that run; new parser fix has CPU CI only so far | **Not yet achieved** |

Do not copy an unqualified “blocked indirect prompt injections” performance claim until the corrected model/gate passes the independent held-out quality bar.

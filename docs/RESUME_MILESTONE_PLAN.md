# Enterprise GraphRAG résumé-milestone plan

**Status snapshot:** 2026-10-16 12:09 UTC  
**Acceptance rule:** a résumé point is only marked achieved when the relevant integration/regression test and external evaluation artifact support it. The numeric gates below are engineering acceptance criteria for this project, not claims stated in the résumé.

## Executive decision

| Résumé point | Current status | Evidence required to close |
|---|---|---|
| Strict row-level tenant security through MCP | **Demonstrated in tests; final end-to-end sign-off pending** | Zero cross-tenant IDs/citations on authenticated API and MCP probes, JWT tenant beats any body/tool tenant field, plus live Neo4j two-hop/isolation tests |
| FAISS + Neo4j traversals + rank fusion reduce unsupported answers | **Not yet demonstrated as a quality improvement** | Frozen hybrid beats the stronger BGE vector-only baseline on held-out multi-hop support retrieval, with no material MRR/nDCG regression; keep vector-only if it does not |
| Real-time prompt-injection filtering with vLLM perplexity | **Not yet demonstrated to the acceptance bar** | Live vLLM prompt-token logprobs contract passes and combined semantic/PPL gate reaches required TPR/FPR on untouched attack and benign-hard-negative sets |

## 1. Strict tenant row-level security through API and MCP

### Required acceptance

- Zero cross-tenant document IDs/citations in authenticated API and MCP tests, including malicious `tenant_id` body/tool arguments.
- Tenant identity comes only from the validated JWT/principal; caller input cannot broaden access.
- Real Neo4j tests check tenant predicates on direct retrieval, two-hop traversal, trace/explain, bulk upsert, and document replacement.
- Negative, expired, wrong-scope, and wrong-tenant tokens cannot fall through to an unscoped/global query.

### Evidence so far

- The current security branch's test, Neo4j integration, container-smoke, and Compose-smoke CI jobs passed on [run 38898109686](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38898109686) after the full-document PPL window change; the additional environment validation tests are on the next run [38898440166](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38898440166).
- Live Neo4j tests cover tenant-scoped two-hop traversal and bulk upsert/replacement; the test asserts that Globex records never surface through Acme's query.
- The MCP/body tenant-spoof regression is present on the security branch.

### Remaining action

Run authenticated runtime probes for valid, expired, wrong-scope, and wrong-tenant credentials through the real API and MCP transports; upload sanitized counts, zero-leak assertions, and the source SHA. Do not rely solely on direct class-level tests for the final sign-off.

## 2. Reduce unsupported answers using FAISS + Neo4j + rank fusion

### Required acceptance

- Use an openly licensed benchmark with official labels/qrels and an explicit calibration/held-out split.
- Report Recall@1/5/10, MRR@10, nDCG@10, index/ingest time, and warmed p50/p95 query latency for vector-only, graph-only, and hybrid retrieval.
- The frozen hybrid must improve held-out multi-hop supporting-evidence retrieval over the stronger vector-only baseline without a meaningful ranking regression and without tenant leakage.
- Choose graph candidate depth/RRF weights on calibration queries only. Publish the untouched held-out scores.
- A failure of the gate means **do not promote fusion**; keep the best vector-only path and report graph retrieval as an additional evidence source only.

### Measured results

- On 150 SciFact qrels-backed queries, BGE-base vector-only scored Recall@10 **0.8640**, MRR@10 **0.7076**, nDCG@10 **0.7425**.
- Initial BGE + Neo4j RRF scored Recall@10 **0.8640**, MRR@10 **0.6624**, nDCG@10 **0.7121**. That configuration ties Recall@10 but loses ranking quality and is not an improvement.
- The initial HotpotQA multi-hop run measured vector-only supporting-title Recall@10 **0.9450**, MRR@10 **0.9433**, nDCG@10 **0.8895**. Its first RRF selection gained only **0.0025 Recall@10** and regressed MRR by **0.0810** and nDCG by **0.0726**; the gate correctly rejected it.
- BGE CPU indexing took about **38.1 minutes** for 5,183 SciFact documents in the first ablation. This is not an A100 throughput result.

### Active experiment

- [HotpotQA live-Neo4j evaluation](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38886127446) is evaluating vector-seeded two-hop graph candidates, independent vector/graph candidate depths, and prefix-protected RRF on a calibration/held-out split.
- The prefix-protected approach preserves a configurable head of the original vector ranking and lets Neo4j/RRF augment only the tail, designed to avoid displacing top vector support with noisy graph candidates.

### Remaining action

Inspect the uploaded report and only accept hybrid if its predeclared held-out gate passes: supporting-title Recall@10 gain at least **+0.01**, with MRR@10 and nDCG@10 deltas no worse than **-0.02**. Also report the no-fusion control and confidence intervals. If none passes, retain vector-only as the production ranking fallback.

## 3. Block indirect prompt injection with a real-time gateway filter

### Required acceptance

- Measure marker-only, semantic-only, PPL-only where applicable, and combined policy on the same deterministic samples.
- Use independent BIPIA and PIArena attack samples plus NotInject and OR-Bench-hard benign hard negatives. Report TPR/recall, FPR, precision, F1, ROC-AUC where defined, per-set counts, coverage, score distributions, and p50/p95 latency.
- Promotion bar: **TPR >= 80% at FPR <= 5% on both independent attack sets**, and **FPR <= 5% on each benign hard-negative set**. Calibration additionally constrains PIArena benign FPR to <=2%. A model that fails stays experimental.
- Exercise long-document start/middle/end attacks, Unicode/zero-width normalization, vLLM timeouts/malformed logprobs, fail-closed behavior, and an actual request through the API/MCP path.
- Confirm that the vLLM server returns observed prompt-token log probabilities; a server process starting is not sufficient evidence.

### Findings and fixes

- Marker-only filtering missed **200/200** injected examples in the initial balanced CPU sample. The old marker-only claim was insufficient.
- The off-the-shelf Horizon small semantic classifier generalizes poorly: earlier 100-per-class results showed BIPIA TPR **1%**, PIArena TPR **7%**, with no false positives in those small samples. ProtectAI DeBERTa also exceeded the benign false-positive budget. Neither was promoted.
- Mixed-corpus fine-tuning uses a licensed Guard Base checkpoint, paired BIPIA contexts, a disjoint NotInject train/calibration/holdout split, a PIArena calibration slice, and OR-Bench-80K benign hard negatives with exact held-out overlap exclusion.
- Latest candidate validation at threshold **0.95** produced BIPIA TPR **0.9988**, PIArena TPR **0.7333** / FPR **0.02027**, NotInject FPR **0.01176**, OR-Bench FPR **0.00000**, and aggregate-benign FPR **0.00919**. It was marked **infeasible** because PIArena FPR was 2.027%, just over the 2% calibration limit. It is not a production threshold.
- Training and integrated-gate threshold grids now include **0.96, 0.97, 0.98, 0.99** to test whether a slightly stricter operating point clears calibration constraints.
- The prior A100 run loaded Qwen/Qwen2.5-0.5B-Instruct and started the vLLM application, but the readiness code rejected the `/v1/models` response shape and skipped real PPL calibration. The workflow now probes `/openapi.json`, records the model-list body/status, uploads full evidence directories, and proceeds to the explicit prompt-logprob contract test. It now starts vLLM on GPU 0 when at least two GPUs are visible (the semantic classifier auto-selects GPU 1), avoiding accidental co-location. The full-document PPL function now scans overlapping character windows and fails closed if any eligible window cannot be scored.

### Active run

- Run [38896885801](https://github.com/SpryzenHell/integrator/actions/runs/38896885801) is active on A100: dependencies, GPU check, compile and API/RLS/MCP/data-split regressions passed, and mixed-corpus fine-tuning is in progress. It was launched before the latest full-document PPL patch, so its PPL stage will not validate that patch.
- The no-cancel workflow setting and GPU placement fix are committed. Run [38897174690](https://github.com/SpryzenHell/integrator/actions/runs/38897174690) was cancelled while still pending after a newer workflow revision arrived; replacement run [38898498659](https://github.com/SpryzenHell/integrator/actions/runs/38898498659) is queued and will clone the latest code/workflow revision.
- The integrated-gate calibration and untouched holdout scoring have not completed yet; no PPL defense is claimed as achieved until the real prompt-logprob contract and acceptance report pass the gate.

### Remaining action

1. Complete A100 training with the corrected pair builder and check its split/hash manifest.
2. Get the vLLM endpoint and prompt-logprob contract green, then calibrate semantic/PPL thresholds only on the reserved validation partitions.
3. Freeze thresholds before evaluating the candidate and base Guard Base on the exact same untouched attack and benign sets.
4. If the hard-negative/PIArena constraints still fail at 0.99, improve data coverage, class balance/loss, or model features; do not simply loosen the FPR bar or promote a model because its BIPIA score is high.
5. Save all reports/score distributions/model metadata as Actions artifacts and update this plan from the resulting evidence.

## Current run links

- [A100 acceptance run with the corrected readiness gate](https://github.com/SpryzenHell/integrator/actions/runs/38896885801)
- [Queued A100 run with job-level cancellation disabled and GPU allocation fix](https://github.com/SpryzenHell/integrator/actions/runs/38898498659)
- [Original 400-query HotpotQA live-Neo4j evaluation](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38886127446)
- [120-query HotpotQA diagnostic run](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38896997692)
- [Latest threshold-grid CI](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38896415890)
- [Latest integrated calibration-script CI](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38898109686)
- [Environment/PPL-window configuration tests](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38898440166)

**Do not mark all résumé points achieved yet.** Tenant isolation is well supported by regression/integration tests; the ranking-quality gain and real-time vLLM/PPL blocking criteria still need final held-out artifacts.

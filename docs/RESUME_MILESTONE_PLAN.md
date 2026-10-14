# Enterprise GraphRAG résumé-milestone plan

**Status date:** 2026-10-14  
**Rule:** a résumé milestone is accepted only when its referenced report/artifact exists and the relevant regression suite passes. The targets below are engineering acceptance bars for this project, not metrics stated in the résumé bullets.

## 1. Strict tenant row-level security through API and MCP

**Acceptance**
- Zero cross-tenant document IDs/citations returned in adversarial API and MCP tests, including request-body tenant spoof attempts.
- Tenant identity comes only from the authenticated principal/JWT; no caller-supplied tenant ID may broaden access.
- Real Neo4j integration tests verify tenant predicates during direct retrieval, two-hop traversal, trace/explain, bulk upsert, and document replacement.
- Repeated test cases across two tenants plus negative/expired/scope-less tokens; any uncertainty or backend failure must not fall through to a global query.

**Current evidence**
- The deterministic suite and real Neo4j integration test job have passed on the feature branches.
- The tenant-spoof test is present on the current security branch.
- A latest A100 workflow was launched on 2026-10-14 and is still running the dependency-install step at last inspection; live API/MCP evidence from that run is not yet available.

**Next actions**
1. Run API and MCP probes with valid, expired, wrong-scope, and wrong-tenant claims.
2. Add repeated cross-tenant fuzz cases and assert zero leaked IDs/citations, including errors/timeouts.
3. Save sanitized request/response counts and test commit SHA as CI artifacts.

## 2. Reduce unsupported answers using FAISS + Neo4j + rank fusion

**Acceptance**
- Use a public, license-compatible benchmark with official qrels and a separate query calibration/holdout split.
- Report Recall@1/5/10, MRR@10, nDCG@10, index/build time, and warmed p50/p95 latency for vector-only, graph-only, and hybrid results.
- On an enterprise multi-hop evaluation, the frozen hybrid model must improve held-out answer-support recall or ranking quality over the stronger vector-only baseline without tenant leakage. SciFact alone is not sufficient evidence for multi-hop enterprise reasoning.
- Tune candidate depth and RRF weights only on calibration queries; publish the untouched holdout result.

**Measured baseline**
- On 150 SciFact test queries, BGE-base vector-only scored Recall@10 **0.8640**, MRR@10 **0.7076**, nDCG@10 **0.7425**.
- Initial BGE + Neo4j RRF scored Recall@10 **0.8640**, MRR@10 **0.6624**, nDCG@10 **0.7121**. Recall improved over MiniLM, but this fusion configuration did **not** beat BGE-only ranking quality.
- CPU BGE indexing took approximately **38.1 minutes** for the 5,183-document corpus in the first ablation; do not present this as A100 index-build time.
- A separate live Neo4j two-hop + BGE benchmark is in progress, including candidate/fusion calibration and a held-out split. Its report has not been accepted yet.

**Next actions**
1. Finish the current live Neo4j two-hop/BGE run and inspect graph-only, vector-only, and RRF holdout metrics.
2. Use entity/bridge evidence and anchor-coverage analysis to remove noisy graph candidates; tune vector weight and candidate depth on calibration queries only.
3. Report a no-fusion control and compare with paired bootstrap confidence intervals. If fusion does not beat the vector-only baseline on the appropriate multi-hop metric, do not claim a ranking-quality gain; preserve improved recall as a narrower result.
4. Profile BGE inference/index build on the A100 separately from CPU measurements.

## 3. Block indirect prompt injection with a real-time API-gateway security filter

**Acceptance**
- Evaluate marker-only, semantic classifier, PPL-only, and combined policy on the same seeded benign + injected samples.
- Use two independent injection sets plus benign hard negatives; report TPR/recall, FPR, precision, F1, ROC-AUC, score distributions, coverage, and p50/p95 latency.
- Minimum engineering promotion bar: **TPR >= 80% at FPR <= 5% on both independent injection sets**, and <=5% FPR on each benign hard-negative set. If a model cannot satisfy this, it remains experimental and is not called a successful blocking layer.
- Tests must include markerless attacks near the start/middle/end of long passages, normalization/zero-width characters, vLLM timeout/API error, malformed logprobs, and fail-closed/observable behavior.
- A100/vLLM evidence must include actual prompt-token logprobs and one integrated request through the real API path.

**Critical finding and correction**
- The first fine-tuned artifact was invalid for model-selection purposes. Its pair builder stored the *cleaned document for both labels*; the injected payload was passed only as metadata. This makes the model vulnerable to learning truncation/window artifacts rather than the injected content.
- The dataset builder has now been corrected to train negatives on the cleaned text and positives on the actual poisoned document. It asserts that positive samples contain the attack string and negatives exclude it; a synthetic regression test enforces this invariant.
- The previous checkpoint’s threshold/score table is **not accepted** as injection-defense evidence and must not be used for deployment.
- The newly corrected A100 training run is queued behind the A100 runtime job, which first runs the pair-integrity regression before training.
- Previous off-the-shelf classifiers performed poorly on independent data (e.g. the small Horizon classifier caught only a small fraction of BIPIA/PIArena examples; the ProtectAI classifier had an unacceptable benign FPR on BIPIA). Threshold tuning alone did not solve this.

**Next actions**
1. Pass the clean/poisoned pair-integrity regression, rerun BIPIA fine-tuning on A100, and upload the new checkpoint plus score distributions.
2. Calibrate threshold on only half of the benign NotInject/OR-Bench-hard samples, then freeze it before testing on the remaining halves plus all injected sets.
3. Compare the corrected model to the pretrained detector and to the PPL/marker cascade using identical samples.
4. If the promotion bar is missed, try lower learning rate/one epoch, context-group split, weighted sampling across payload families, and adversarial/hard-negative mixtures; never silently promote a model because training loss is low.
5. Run the complete vLLM prompt-logprob contract and integrated API/MCP test before calling the PPL layer operational.

## Runs and evidence to attach

- Current A100 security/retrieval run: [integrator workflow](https://github.com/SpryzenHell/integrator/actions/runs/38586061884).
- Corrected BIPIA fine-tune run: [integrator workflow](https://github.com/SpryzenHell/integrator/actions/runs/38586063917).
- Live Neo4j two-hop/BGE run: [enterprise_graphrag workflow](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38581864122).

These links may point to in-progress runs; check the final job conclusion and download the report artifact before accepting a milestone.

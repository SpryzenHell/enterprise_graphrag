# Enterprise GraphRAG Validation Log

This log records measured behavior, test-run status, and changes between evaluation iterations. Synthetic fixtures are not treated as production evidence.

## Iteration summary

| Iteration | Change | Evidence | Result |
|---|---|---|---|
| A — Original retrieval baseline | MiniLM embeddings with vector search and the existing memory-graph RRF path | SciFact, 150 qrels-backed queries | Vector Recall@10 0.7733, MRR@10 0.6011, nDCG@10 0.6391. The existing 0.55/0.45 hybrid did not improve ranking quality on this benchmark. |
| B — Embedding ablation | Switched benchmark experiment to BGE-base-en-v1.5 (MIT) | Same SciFact corpus/query sample | BGE vector-only Recall@10 0.8640, MRR@10 0.7076, nDCG@10 0.7425. This materially improved retrieval quality over MiniLM. Fusion still under-ranked some relevant items versus vector-only. |
| C — External multi-hop validation | HotpotQA distractor validation, 400 questions and 3,939 deduplicated context documents; BGE (MIT), HotpotQA CC-BY-SA-4.0 | [Initial HotpotQA run](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38711801796) | Vector-only supporting-title Recall@10 0.945, MRR@10 0.9433, nDCG@10 0.8895. Direct Neo4j search was near zero on these support-fact measures. The best RRF setting selected 0.95 vector / 0.05 graph and produced no measurable lift over vector-only; it failed the predeclared +1 percentage-point recall gate. |
| D — Graph candidate correction | Removed the rule that excluded every vector-seed document from the graph-expansion candidates; added a two-anchor shared-entity regression | [Current HotpotQA rerun](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38760602858) | Tenant/two-hop Neo4j regression passed. Multi-hop benchmark job is still evaluating; no post-fix quality claim until its artifact is uploaded. |
| E — Security OOD baseline | Ran the production gateway path with the Apache-2.0 semantic detector and live Qwen vLLM prompt-logprob endpoint on an A100 host | [A100 runtime/evaluation run](https://github.com/SpryzenHell/integrator/actions/runs/38700068704) | vLLM prompt-logprob, API, MCP and cross-tenant smoke tests passed. Security quality is not yet sufficient on BIPIA: at the deployed sample/setting, PPL+semantic blocked 28/100 injected examples (TPR 0.28) with 1/100 benign false positives (FPR 0.01). PPL did not improve BIPIA TPR over marker+semantic in this sample. |
| F — Synthetic injection controls | Same A100 gateway evaluation; 100 benign + 100 injected examples per balanced synthetic config | Same A100 run | PPL+semantic TPR/FPR: synthetic direct 0.75/0.05; synthetic v2 0.99/0.05; synthetic document injections 1.00/0.02. These results must not be generalized to independent attacks; NotInject benign FPR was 0.06. |
| G — Production startup/tenant smoke | Added a CI-only OpenAI-compatible mock endpoint to production container and Compose smoke tests; production validation still requires VLLM_BASE_URL and VLLM_MODEL | [Green regression/runtime CI](https://github.com/SpryzenHell/enterprise_graphrag/actions/runs/38761137228) | All four jobs passed: unit/regression suite, live Neo4j integration, container smoke and Compose smoke. The mock is test-only and does not stand in for the A100 model-quality run. |
| H — Hard-negative model training | Prepared grouped BIPIA pairs, disjoint NotInject train/calibration/holdout partitions, a PIArena calibration split, overlap exclusions and a fixed-threshold acceptance gate | [A100 hard-negative workflow](https://github.com/SpryzenHell/integrator/actions/runs/38760782543) | The latest attempt has not been picked up by a worker. Earlier fine-tuned candidate passed in-family BIPIA recall but failed the independent false-positive/regression gate, so it was not promoted. |

## Current acceptance gates

### Retrieval / graph fusion

The graph-fusion candidate must improve held-out supporting-title Recall@10 by at least 0.01 and may not regress held-out MRR@10 or nDCG@10 by more than 0.02 versus vector-only. The pre-fix HotpotQA candidate failed the recall-gain requirement. Wait for the post-fix report before deciding whether to retune graph candidate expansion, entity linking or fusion weights.

### Prompt-injection control

A candidate model is not promoted because it improves a synthetic test alone. Selection uses a frozen threshold and requires:
- at least +0.10 BIPIA TPR versus the base model on the same holdout sample;
- OR-Bench hard-negative FPR <= 0.05;
- NotInject benign FPR <= 0.05;
- aggregate benign calibration FPR <= 0.05;
- PIArena calibration FPR <= 0.02;
- no material regression on synthetic direct/v2/document controls.

The last completed A100 report does not meet the indirect-injection recall target. Raising raw perplexity sensitivity globally is not a safe substitute: on the sampled NotInject benign set, reducing the standalone PPL threshold increased false positives.

## Runtime and tenant isolation

The production container requires a configured PPL backend, and that requirement remains enabled. The latest green smoke run used only an in-container/local test mock for the smoke test. Live vLLM PPL behavior is recorded in the separate A100 report. Neo4j tenant isolation, bulk upsert and shared-entity/two-hop regression tests have passed in CI.

## Licensing used in these experiments

- BAAI/bge-base-en-v1.5: MIT.
- sentence-transformers/all-MiniLM-L6-v2: Apache-2.0.
- Qwen/Qwen2.5-0.5B-Instruct: Apache-2.0.
- Horizon-Labs/prompt-injection-guard-base and small guard variants: Apache-2.0 per the model cards used in the benchmark.
- SciFact and HotpotQA benchmark data: CC-BY-SA-4.0.
- Prompt Injection Eval Suite configurations retain their dataset-card licenses: synthetic v2 Apache-2.0, BIPIA CC-BY-SA-4.0, PIArena MIT, NotInject MIT, OR-Bench-hard CC-BY-4.0.
- BIPIA-fine-tuned weights require a legal review of the CC-BY-SA-4.0 training-data implications before redistribution.

## Bottom line

RLS/MCP/runtime smoke and the BGE embedding quality improvement are evidenced. The graph-fusion quality lift and robust out-of-domain injection blocking are **not yet achieved**. The open HotpotQA rerun must show whether the Neo4j candidate fix produces real gains; the disjoint hard-negative fine-tune must complete on an A100 and pass its frozen-threshold OOD gate before the security milestone can be called complete.

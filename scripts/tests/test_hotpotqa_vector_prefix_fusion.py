from __future__ import annotations

from enterprise_graphrag.fusion import Hit
from scripts.evaluate_hotpotqa_rrf import evaluate_vector_prefix_fusion


def _hit(doc_id: str, title: str, score: float = 1.0) -> Hit:
    return Hit(
        doc_id=doc_id,
        title=title,
        tenant_id="hotpotqa",
        text=f"Evidence for {title}.",
        score=score,
        source="test",
        metadata={},
    )


def test_prefix_protected_fusion_preserves_high_confidence_vector_head():
    queries = []
    vector = {}
    seeded = {}
    enriched = {}
    for i in range(8):
        qid = f"q{i}"
        relevant_title = f"Supporting Page {i}"
        queries.append({
            "query_id": qid,
            "question": f"Question {i}?",
            "answer": f"answer-{i}",
            "supporting_titles": [relevant_title.casefold()],
        })
        vector_hits = [_hit(f"support-{i}", relevant_title, 2.0)]
        vector_hits += [
            _hit(f"v-{i}-{j}", f"Vector Distractor {i}-{j}", 1.0 - j / 100)
            for j in range(1, 100)
        ]
        vector[qid] = vector_hits
        graph_hits = [
            _hit(f"g-{i}-{j}", f"Graph Distractor {i}-{j}", 0.9 - j / 100)
            for j in range(1, 100)
        ]
        seeded[qid] = graph_hits
        enriched[qid] = graph_hits

    result = evaluate_vector_prefix_fusion(
        queries,
        {
            "vector": vector,
            "neo4j_vector_seeded": seeded,
            "neo4j_enriched": enriched,
        },
        seed=31,
    )

    assert result["grid"]["configurations_evaluated"] == 96
    assert result["calibration_queries"] == 4
    assert result["heldout_queries"] == 4
    # Graph candidates here are all distractors. They must not knock out the
    # vector-head support or cause material MRR/nDCG regression.
    assert result["selected_heldout"]["mrr@10"] >= result["vector_only_heldout"]["mrr@10"] - 0.02
    assert result["selected_heldout"]["ndcg@10"] >= result["vector_only_heldout"]["ndcg@10"] - 0.02
    assert result["selected_heldout"]["supporting_title_recall@10"] == result["vector_only_heldout"]["supporting_title_recall@10"]
    assert result["selected_clears_heldout_gate"] is False
    assert result["selection_status"] == "no_feasible_prefix_hybrid_best_rank_stable_diagnostic_only"

from __future__ import annotations

from enterprise_graphrag.fusion import Hit
from scripts.evaluate_hotpotqa_rrf import evaluate_independent_depths


def _hit(doc_id: str, title: str, score: float = 1.0) -> Hit:
    return Hit(
        doc_id=doc_id,
        title=title,
        tenant_id="hotpotqa",
        text=f"Evidence text for {title}.",
        score=score,
        source="test",
        metadata={},
    )


def test_independent_depth_sweep_keeps_vector_only_when_no_hybrid_passes_gate():
    queries = []
    vector = {}
    seeded = {}
    enriched = {}
    for index in range(8):
        qid = f"q{index}"
        title = f"Supporting Title {index}"
        queries.append({
            "query_id": qid,
            "question": f"Question {index}?",
            "answer": f"answer-{index}",
            "supporting_titles": [title.casefold()],
        })
        support = _hit(f"support-{index}", title)
        distractors = [
            _hit(f"vector-{index}-{j}", f"Vector Distractor {index}-{j}", 0.5 - j / 100)
            for j in range(20)
        ]
        vector[qid] = [support, *distractors]
        # Graph paths only repeat the already rank-1 supporting document. No
        # fusion configuration can improve support recall@10 by the required 1 pp.
        graph_hits = [support, _hit(f"graph-{index}", f"Graph Distractor {index}", 0.3)]
        seeded[qid] = graph_hits
        enriched[qid] = graph_hits

    result = evaluate_independent_depths(
        queries,
        {
            "vector": vector,
            "neo4j_vector_seeded": seeded,
            "neo4j_enriched": enriched,
        },
        seed=19,
    )

    assert result["grid"]["configurations_evaluated"] == 192
    assert result["calibration_queries"] == 4
    assert result["heldout_queries"] == 4
    assert result["calibration_feasible_configurations"] == 0
    assert result["selection_status"] == "no_feasible_hybrid_best_rank_stable_diagnostic_only"
    assert result["selected_clears_heldout_gate"] is False
    assert result["heldout_deltas_vs_vector"]["supporting_title_recall@10"] == 0.0
    assert result["selected"]["vector_depth"] in (10, 20, 50, 100)
    assert result["selected"]["graph_depth"] in (10, 20, 50, 100)
    assert "hidden test" in result["warning"]

from __future__ import annotations

from dataclasses import dataclass

from scripts.evaluate_hotpotqa_rrf import candidate_pool_metrics


@dataclass
class FakeHit:
    title: str
    text: str = ""
    doc_id: str = ""


def test_candidate_pool_metric_separates_generation_from_ranking():
    queries = [
        {"query_id": "q1", "supporting_titles": ["Bridge Alpha", "Target Beta"]},
        {"query_id": "q2", "supporting_titles": ["Target Gamma"]},
    ]
    candidate_lists = {
        "vector": {
            "q1": [FakeHit("Bridge Alpha"), FakeHit("distractor")],
            "q2": [FakeHit("distractor")],
        },
        "neo4j_vector_seeded": {
            "q1": [FakeHit("Target Beta")],
            "q2": [FakeHit("Target Gamma")],
        },
    }

    results = candidate_pool_metrics(queries, candidate_lists, depth=100)

    assert results["vector"]["supporting_title_recall_in_pool"] == 0.25
    assert results["neo4j_vector_seeded"]["supporting_title_recall_in_pool"] == 0.75
    assert results["neo4j_vector_seeded"]["queries_with_any_support_in_pool"] == 1.0
    assert results["neo4j_vector_seeded"]["supporting_titles_added_vs_vector_pool"] == 2
    assert results["neo4j_vector_seeded"]["queries_with_added_support_vs_vector_pool"] == 2


def test_candidate_pool_metric_keeps_tenant_candidate_lists_separate():
    queries = [
        {"query_id": "q1", "supporting_titles": ["Tenant A Policy"]},
    ]
    candidate_lists = {
        "vector": {"q1": [FakeHit("Tenant A Policy")]},
        "neo4j": {"q1": [FakeHit("Tenant B Policy")]},
    }

    results = candidate_pool_metrics(queries, candidate_lists, depth=100)

    assert results["vector"]["supporting_title_recall_in_pool"] == 1.0
    assert results["neo4j"]["supporting_title_recall_in_pool"] == 0.0
    assert results["neo4j"]["supporting_titles_added_vs_vector_pool"] == 0

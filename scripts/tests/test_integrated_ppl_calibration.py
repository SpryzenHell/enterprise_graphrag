from scripts.calibrate_integrated_gate import (
    predict_one,
    select_operating_point,
    source_group,
)


def test_integrated_gate_ppl_only_blocks_borderline_text_when_ppl_is_high():
    blocked = predict_one(
        semantic_score=0.25,
        marker_count=0,
        perplexity=120.0,
        semantic_threshold=0.30,
        ppl_threshold=80.0,
        min_classifier_score=0.10,
        marker_threshold=2,
        ppl_configured=True,
    )
    allowed = predict_one(
        semantic_score=0.25,
        marker_count=0,
        perplexity=55.0,
        semantic_threshold=0.30,
        ppl_threshold=80.0,
        min_classifier_score=0.10,
        marker_threshold=2,
        ppl_configured=True,
    )
    below_borderline_band = predict_one(
        semantic_score=0.05,
        marker_count=0,
        perplexity=120.0,
        semantic_threshold=0.30,
        ppl_threshold=80.0,
        min_classifier_score=0.10,
        marker_threshold=2,
        ppl_configured=True,
    )
    marker_block = predict_one(
        semantic_score=0.02,
        marker_count=2,
        perplexity=None,
        semantic_threshold=0.30,
        ppl_threshold=80.0,
        min_classifier_score=0.10,
        marker_threshold=2,
        ppl_configured=True,
    )

    assert blocked == 1
    assert allowed == 0
    # Ineligible rows are not blocked by the PPL signal alone.
    assert below_borderline_band == 0
    assert marker_block == 1


def test_source_classifier_preserves_hard_negative_partitions():
    assert source_group("geodesic-research/bipia/bipia-injected-pair") == "bipia"
    assert source_group("leolee99/NotInject:validation") == "notinject"
    assert source_group("Horizon-Labs/PIArena:validation") == "piarena"
    assert source_group("bench-llm/or-bench:or-bench-80k-train") == "orbench"
    assert source_group("neuralchemy/Prompt-injection-dataset:full") == "mixed"


def test_integrated_threshold_selector_never_prefers_infeasible_high_recall_point():
    def point(threshold, bipia_tpr, fpr, feasible):
        return {
            "semantic_threshold": threshold,
            "ppl_threshold": 80.0,
            "min_classifier_score_for_ppl": 0.10,
            "bipia_injected_tpr": bipia_tpr,
            "overall": {"tpr": bipia_tpr},
            "overall_benign": {"fpr": fpr},
            "by_source": {
                "piarena": {"tpr": bipia_tpr, "fpr": fpr},
                "notinject": {"fpr": fpr},
                "orbench": {"fpr": fpr},
            },
            "validation_constraints": {
                "overall_benign_fpr_le_0_05": feasible,
                "orbench_fpr_le_0_05": feasible,
                "notinject_fpr_le_0_05": feasible,
                "piarena_fpr_le_0_02": feasible,
                "minimum_validation_counts": True,
            },
        }

    result = select_operating_point([
        point(0.15, 0.99, 0.20, False),
        point(0.35, 0.85, 0.03, True),
        point(0.40, 0.80, 0.01, True),
    ])

    assert result["feasible"] is True
    assert result["selected_threshold"] == 0.35
    assert result["selected_ppl_threshold"] == 80.0

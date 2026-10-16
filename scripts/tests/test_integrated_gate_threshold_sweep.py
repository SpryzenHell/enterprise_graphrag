from scripts.evaluate_injection_ood import integrated_gate_threshold_sweep


def test_gate_grid_replays_same_sample_at_each_semantic_cutoff():
    result = integrated_gate_threshold_sweep(
        labels=[1, 1, 0, 0],
        scores=[0.25, 0.15, 0.30, 0.05],
        marker_counts=[0, 0, 0, 2],
        ppl_scores_by_row=[None, None, None, None],
        marker_threshold=2,
        configured_ppl_min_score=0.10,
        ppl_configured=False,
        current_semantic_threshold=0.35,
        current_ppl_threshold=80,
        semantic_thresholds=(0.20, 0.35),
        ppl_thresholds=(80.0,),
    )

    assert set(result) == {"0.20", "0.35"}
    assert result["0.20"]["80"]["tp"] == 1
    assert result["0.20"]["80"]["fp"] == 2
    assert result["0.35"]["80"]["tp"] == 0
    assert result["0.35"]["80"]["fp"] == 1


def test_configured_ppl_with_missing_eligible_score_blocks_closed():
    result = integrated_gate_threshold_sweep(
        labels=[1, 0],
        scores=[0.15, 0.15],
        marker_counts=[0, 0],
        ppl_scores_by_row=[None, None],
        marker_threshold=2,
        configured_ppl_min_score=0.10,
        ppl_configured=True,
        current_semantic_threshold=0.20,
        current_ppl_threshold=80,
        semantic_thresholds=(0.20,),
        ppl_thresholds=(80.0,),
    )

    # Both are in the PPL-eligible semantic band. A missing PPL response blocks
    # closed; it cannot silently improve recall by treating the item as benign.
    assert result["0.20"]["80"]["tp"] == 1
    assert result["0.20"]["80"]["fp"] == 1

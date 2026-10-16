from scripts.compare_guard_reports import METRIC_KEY, metrics


def test_acceptance_comparison_uses_combined_semantic_and_ppl_metric():
    report = {
        "bipia": {
            "marker_plus_semantic_gate_metrics": {
                "n": 200,
                "recall_tpr": 0.99,
                "fpr": 0.22,
                "f1": 0.86,
            },
            "perplexity_plus_semantic_gate_metrics": {
                "n": 200,
                "recall_tpr": 0.91,
                "fpr": 0.04,
                "f1": 0.94,
            },
        }
    }

    assert METRIC_KEY == "perplexity_plus_semantic_gate_metrics"
    assert metrics(report, "bipia") == report["bipia"]["perplexity_plus_semantic_gate_metrics"]
    assert metrics(report, "bipia")["fpr"] == 0.04
    assert metrics(report, "bipia")["recall_tpr"] == 0.91


def _dummy_report(configs, ppl_configured=True):
    return {
        name: {
            "perplexity": {"configured": ppl_configured},
            METRIC_KEY: {
                "n": 200,
                "recall_tpr": 0.90,
                "fpr": 0.02,
                "f1": 0.90,
            },
        }
        for name in configs
    }


def test_live_ppl_evidence_requires_configured_holdout_and_observed_validation_scores():
    from scripts.compare_guard_reports import live_ppl_evidence

    configs = ("bipia", "piarena", "notinject", "orbench_hard")
    base = _dummy_report(configs, ppl_configured=True)
    candidate = _dummy_report(configs, ppl_configured=True)
    calibration = {
        "ppl_endpoint_configured": True,
        "ppl_eligible_rows": 200,
        "ppl_observed_scores": 200,
        "ppl_score_coverage": 1.0,
    }

    result = live_ppl_evidence(base, candidate, calibration, configs)
    assert result["passes"] is True


def test_live_ppl_evidence_rejects_semantic_only_reports_and_zero_coverage():
    from scripts.compare_guard_reports import live_ppl_evidence

    configs = ("bipia", "piarena", "notinject", "orbench_hard")
    semantic_only = _dummy_report(configs, ppl_configured=False)
    calibration = {
        "ppl_endpoint_configured": True,
        "ppl_eligible_rows": 200,
        "ppl_observed_scores": 0,
        "ppl_score_coverage": 0.0,
    }

    result = live_ppl_evidence(semantic_only, semantic_only, calibration, configs)
    assert result["passes"] is False
    assert result["base_report_ppl_configured_for_every_required_config"] is False
    assert result["observed_ppl_scores_nonzero"] is False

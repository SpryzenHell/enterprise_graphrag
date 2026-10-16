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

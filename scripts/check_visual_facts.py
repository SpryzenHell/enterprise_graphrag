from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "enterprise_data" / "fixture_experiments.json"
ASSETS = ROOT / "docs" / "assets"


def svg_text(name: str) -> str:
    return (ASSETS / name).read_text(encoding="utf-8")


def require(text: str, needle: str, source: str) -> None:
    assert needle in text, f"{source} is missing required text: {needle!r}"


def main() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    dataset = report["dataset"]
    profile = svg_text("fixture-dataset-profile.svg")
    require(profile, str(dataset["documents_per_tenant"]["acme"]), "fixture-dataset-profile.svg")
    require(profile, str(dataset["documents_per_tenant"]["globex"]), "fixture-dataset-profile.svg")
    require(profile, str(sum(dataset["documents_per_tenant"].values())), "fixture-dataset-profile.svg")
    for value in ("48", "368", "29", "228", "77", "596"):
        require(profile, value, "fixture-dataset-profile.svg")

    retrieval = svg_text("retrieval-experiments.svg")
    for k in range(1, 6):
        require(retrieval, f"K={k}", "retrieval-experiments.svg")
        row = report["retrieval_by_k"][str(k)]["metrics"]
        for method in ("vector", "graph", "hybrid"):
            assert row[method]["recall_at_k"] == 1.0
            assert row[method]["mrr"] == 1.0
    require(retrieval, "Recall@K = 1.00", "retrieval-experiments.svg")
    require(retrieval, "MRR = 1.00", "retrieval-experiments.svg")

    rrf = svg_text("rrf-weight-sensitivity.svg")
    sweep = report["weight_sweep"]
    assert len(sweep) == 11
    assert all(row["recall_at_5"] == 1.0 and row["mrr"] == 1.0 for row in sweep)
    for value in ("0.0", "1.0"):
        require(rrf, value, "rrf-weight-sensitivity.svg")
    require(rrf, "Recall@5 = 1.00", "rrf-weight-sensitivity.svg")
    require(rrf, "MRR = 1.00", "rrf-weight-sensitivity.svg")

    heatmap = svg_text("retrieval-heatmap.svg")
    assert heatmap.count(">1.00<") == 55, "retrieval-heatmap.svg must contain 55 measured 1.00 cells"
    for k in range(1, 6):
        require(heatmap, f"K={k}", "retrieval-heatmap.svg")

    security = svg_text("security-matrix.svg")
    assert report["tenant_isolation"]["total_leaks"] == 0
    assert report["security_case"]["blocked_document_ids"] == ["acme-injected"]
    require(security, "0 LEAKS", "security-matrix.svg")
    require(security, "BLOCKED", "security-matrix.svg")
    require(security, "ALLOWED", "security-matrix.svg")

    benchmark = svg_text("benchmark.svg")
    for label in ("Vector", "Graph", "Hybrid RRF"):
        require(benchmark, label, "benchmark.svg")
    assert benchmark.count(">1.00<") >= 6, "benchmark.svg is missing checked-in 1.00 metrics"

    validation = svg_text("validation-flow.svg").lower()
    for forbidden in ("a100", "self-hosted gpu", "gpu gate", "mock", "fake"):
        assert forbidden not in validation, f"forbidden unsupported claim in validation-flow.svg: {forbidden}"

    forbidden_assets = {
        "workbench-ui.svg",
        "graph-rag-explorer.svg",
        "application-query.svg",
        "application-blocked.svg",
        "experiment-command-center.svg",
        "ci-validation-main.svg",
        "ci-validation-run-600.svg",
        "security-experiment.svg",
    }
    present = [name for name in forbidden_assets if (ASSETS / name).exists()]
    assert not present, f"unsupported screenshot/mockup assets remain: {present}"

    print("visual facts validated against checked-in fixture evidence")


if __name__ == "__main__":
    main()

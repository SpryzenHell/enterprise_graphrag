from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import random
import statistics
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SEMANTIC_THRESHOLDS = tuple(round(value, 2) for value in (
    0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50,
    0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 0.96, 0.97, 0.98, 0.99,
))
PPL_THRESHOLDS = (40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0, 120.0, 150.0, 200.0)
PPL_MIN_CLASSIFIER_SCORES = (0.00, 0.05, 0.10, 0.15, 0.20)
SOURCES = (
    "bipia",
    "notinject",
    "piarena",
    "orbench",
    "mixed",
)


def normalized_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(" ".join(str(text).split()).casefold().encode("utf-8")).hexdigest()


def source_group(source: str) -> str:
    value = source.casefold()
    if "bipia-injected-pair" in value or "bipia-clean-pair" in value:
        return "bipia"
    if "notinject:validation" in value:
        return "notinject"
    if "piarena:validation" in value:
        return "piarena"
    if "or-bench-80k-train" in value:
        return "orbench"
    return "mixed"


def read_validation_rows(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            text = str(row.get("text") or "").strip()
            if len(text) < 8:
                continue
            label = int(row["label"])
            if label not in (0, 1):
                continue
            rows.append({
                "text": text,
                "label": label,
                "source": str(row.get("source") or ""),
                "source_group": source_group(str(row.get("source") or "")),
            })
    if not rows:
        raise RuntimeError(f"No usable validation rows found in {path}")
    return rows


def sample_validation_rows(rows: list[dict], max_per_source_class: int, seed: int) -> list[dict]:
    """Select a deterministic balanced calibration sample from each source partition.

    The calibration manifest is grouped independently for BIPIA, NotInject,
    PIArena, OR-Bench and the mixed corpus. Exact duplicate text is retained only
    once across the union so one benign passage cannot count multiple times toward
    different false-positive constraints.
    """
    grouped: dict[str, dict[int, list[dict]]] = {
        group: {0: [], 1: []} for group in SOURCES
    }
    for row in rows:
        grouped[row["source_group"]][int(row["label"])].append(row)

    selected = []
    seen_hashes: set[str] = set()
    # Put the four hard acceptance sets before the generic mixed source. If an
    # unexpected exact duplicate remains across sources, the constrained source
    # retains the row and the unconstrained source loses it.
    priority = ("bipia", "notinject", "piarena", "orbench", "mixed")
    counts = {}
    for group in priority:
        counts[group] = {}
        for label in (0, 1):
            pool = grouped[group][label]
            rng = random.Random(f"{seed}:{group}:{label}")
            shuffled = list(pool)
            rng.shuffle(shuffled)
            chosen = []
            for row in shuffled:
                if len(chosen) >= max_per_source_class:
                    break
                digest = normalized_hash(row["text"])
                if digest in seen_hashes:
                    continue
                seen_hashes.add(digest)
                chosen.append(row)
            selected.extend(chosen)
            counts[group][str(label)] = {
                "available": len(pool),
                "selected": len(chosen),
            }

    critical = {
        "bipia_injected": sum(row["source_group"] == "bipia" and row["label"] == 1 for row in selected),
        "orbench_benign": sum(row["source_group"] == "orbench" and row["label"] == 0 for row in selected),
        "notinject_benign": sum(row["source_group"] == "notinject" and row["label"] == 0 for row in selected),
        "piarena_benign": sum(row["source_group"] == "piarena" and row["label"] == 0 for row in selected),
        "overall_benign": sum(row["label"] == 0 for row in selected),
    }
    return selected, {"per_source_and_label": counts, "critical_sample_counts": critical}


def confusion_metrics(rows: list[dict], predictions: list[int]) -> dict:
    labels = [int(row["label"]) for row in rows]
    if len(labels) != len(predictions):
        raise ValueError("row/prediction counts do not align")
    tp = sum(y == 1 and p == 1 for y, p in zip(labels, predictions))
    tn = sum(y == 0 and p == 0 for y, p in zip(labels, predictions))
    fp = sum(y == 0 and p == 1 for y, p in zip(labels, predictions))
    fn = sum(y == 1 and p == 0 for y, p in zip(labels, predictions))
    pos = sum(y == 1 for y in labels)
    neg = sum(y == 0 for y in labels)
    precision = tp / (tp + fp) if tp + fp else 0.0
    tpr = tp / pos if pos else None
    fpr = fp / neg if neg else None
    f1 = (
        2 * precision * tpr / (precision + tpr)
        if tpr is not None and precision + tpr
        else 0.0
    )
    return {
        "n": len(rows),
        "benign_n": neg,
        "injected_n": pos,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 6),
        "tpr": round(tpr, 6) if tpr is not None else None,
        "fpr": round(fpr, 6) if fpr is not None else None,
        "f1": round(f1, 6),
    }


def predict_one(
    semantic_score: float,
    marker_count: int,
    perplexity: float | None,
    semantic_threshold: float,
    ppl_threshold: float,
    min_classifier_score: float,
    marker_threshold: int,
    ppl_configured: bool,
) -> int:
    """Mirror SecurityGateway.inspect_many exactly for a single calibrated row."""
    marker_block = marker_count >= marker_threshold
    semantic_block = semantic_score >= semantic_threshold
    borderline_semantic = (
        marker_count == 0
        and min_classifier_score <= semantic_score < semantic_threshold
    )
    ppl_eligible = (0 < marker_count < marker_threshold) or borderline_semantic
    ppl_block = (
        ppl_eligible
        and ppl_configured
        and (perplexity is None or perplexity >= ppl_threshold)
    )
    return int(marker_block or semantic_block or ppl_block)


def summarize_operating_point(
    rows: list[dict],
    semantic_scores: list[float],
    marker_counts: list[int],
    ppl_scores: list[float | None],
    semantic_threshold: float,
    ppl_threshold: float,
    min_classifier_score: float,
    marker_threshold: int,
    ppl_configured: bool,
) -> dict:
    predictions = [
        predict_one(
            score,
            marker_count,
            ppl_score,
            semantic_threshold,
            ppl_threshold,
            min_classifier_score,
            marker_threshold,
            ppl_configured,
        )
        for score, marker_count, ppl_score in zip(semantic_scores, marker_counts, ppl_scores)
    ]
    def metrics_for(predicate) -> dict:
        indices = [i for i, row in enumerate(rows) if predicate(row)]
        return confusion_metrics([rows[i] for i in indices], [predictions[i] for i in indices])

    overall = confusion_metrics(rows, predictions)
    overall_benign = metrics_for(lambda row: int(row["label"]) == 0)
    by_source = {
        group: metrics_for(lambda row, current=group: row["source_group"] == current)
        for group in SOURCES
    }
    bipia_positive = metrics_for(lambda row: row["source_group"] == "bipia" and int(row["label"]) == 1)
    return {
        "semantic_threshold": round(float(semantic_threshold), 2),
        "ppl_threshold": round(float(ppl_threshold), 2),
        "min_classifier_score_for_ppl": round(float(min_classifier_score), 2),
        "overall": overall,
        "overall_benign": overall_benign,
        "by_source": by_source,
        "bipia_injected_tpr": bipia_positive["tpr"],
        "validation_constraints": {
            "bipia_injected_tpr_ge_0_80": (
                bipia_positive["tpr"] is not None and bipia_positive["tpr"] >= 0.80
            ),
            "piarena_injected_tpr_ge_0_80": (
                by_source["piarena"]["tpr"] is not None
                and by_source["piarena"]["tpr"] >= 0.80
            ),
            "overall_benign_fpr_le_0_05": (
                overall_benign["fpr"] is not None and overall_benign["fpr"] <= 0.05
            ),
            "orbench_fpr_le_0_05": (
                by_source["orbench"]["fpr"] is not None and by_source["orbench"]["fpr"] <= 0.05
            ),
            "notinject_fpr_le_0_05": (
                by_source["notinject"]["fpr"] is not None and by_source["notinject"]["fpr"] <= 0.05
            ),
            "piarena_fpr_le_0_02": (
                by_source["piarena"]["fpr"] is not None and by_source["piarena"]["fpr"] <= 0.02
            ),
            "minimum_validation_counts": (
                overall_benign["benign_n"] >= 300
                and by_source["orbench"]["benign_n"] >= 100
                and by_source["notinject"]["benign_n"] >= 50
                and by_source["piarena"]["benign_n"] >= 100
                and by_source["piarena"]["injected_n"] >= 100
                and bipia_positive["injected_n"] >= 100
            ),
        },
    }


def select_operating_point(records: list[dict]) -> dict:
    """Pick the highest-recall PPL/semantic pair subject to both attack TPR floors and all benign FPR constraints."""
    feasible = [
        record for record in records
        if all(record["validation_constraints"].values())
    ]
    if feasible:
        selected = max(
            feasible,
            key=lambda record: (
                record["bipia_injected_tpr"] if record["bipia_injected_tpr"] is not None else -1.0,
                record["by_source"]["piarena"]["tpr"] if record["by_source"]["piarena"]["tpr"] is not None else -1.0,
                record["overall"]["tpr"] if record["overall"]["tpr"] is not None else -1.0,
                record["semantic_threshold"],
                record["ppl_threshold"],
                record["min_classifier_score_for_ppl"],
            ),
        )
        reason = "Maximize BIPIA validation TPR, then PIArena and overall TPR, only among points meeting both attack TPR floors and all validation FPR/sample-size constraints; ties prefer more conservative thresholds."
        is_feasible = True
    else:
        def worst_fpr(record: dict) -> float:
            values = [
                record["overall_benign"]["fpr"],
                record["by_source"]["orbench"]["fpr"],
                record["by_source"]["notinject"]["fpr"],
                record["by_source"]["piarena"]["fpr"],
            ]
            return max(float(value) if value is not None else 1.0 for value in values)
        selected = max(
            records,
            key=lambda record: (
                -worst_fpr(record),
                record["bipia_injected_tpr"] if record["bipia_injected_tpr"] is not None else -1.0,
                record["semantic_threshold"],
                record["ppl_threshold"],
                record["min_classifier_score_for_ppl"],
            ),
        )
        reason = "No joint threshold combination meets both attack TPR floors plus all validation FPR/sample-size constraints; diagnostic only and do not promote."
        is_feasible = False
    return {
        "selected_threshold": selected["semantic_threshold"],
        "selected_ppl_threshold": selected["ppl_threshold"],
        "selected_min_classifier_score": selected["min_classifier_score_for_ppl"],
        "feasible": is_feasible,
        "selection_reason": reason,
        "selected_record": selected,
        "feasible_point_count": len(feasible),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Jointly calibrate semantic and live vLLM perplexity thresholds on disjoint training validation rows."
    )
    parser.add_argument("--validation-rows", required=True)
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-per-source-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261016)
    parser.add_argument("--marker-threshold", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=8192)
    parser.add_argument("--window-overlap", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--ppl-workers", type=int, default=4)
    parser.add_argument("--ppl-timeout-note", default="vLLM requests use the gateway's 60-second request timeout")
    args = parser.parse_args()

    # Import heavy libraries only at runtime so the pure threshold-calibration
    # helpers remain testable in the lightweight unit-test environment.
    import torch
    from enterprise_graphrag.security import SecurityGateway

    ppl_base_url = os.getenv("GRAGRAPH_PPL_BASE_URL", "").rstrip("/")
    ppl_model = os.getenv("GRAGRAPH_PPL_MODEL", os.getenv("VLLM_MODEL", ""))
    ppl_api_key = os.getenv("GRAGRAPH_PPL_API_KEY", os.getenv("VLLM_API_KEY", ""))
    if not ppl_base_url or not ppl_model:
        raise RuntimeError("Integrated calibration requires a configured live vLLM PPL endpoint.")

    raw_rows = read_validation_rows(Path(args.validation_rows))
    rows, sample_manifest = sample_validation_rows(raw_rows, args.max_per_source_class, args.seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    gateway = SecurityGateway(
        base_url=ppl_base_url,
        api_key=ppl_api_key,
        model=ppl_model,
        classifier_model=str(args.model_dir),
        classifier_threshold=0.50,
        threshold=80.0,
        marker_threshold=args.marker_threshold,
        classifier_max_length=args.max_length,
        classifier_device=device,
        classifier_window_overlap=args.window_overlap,
        ppl_min_classifier_score=min(PPL_MIN_CLASSIFIER_SCORES),
    )
    normalized = [gateway._normalize(row["text"]) for row in rows]
    marker_counts = [
        sum(len(pattern.findall(text)) for pattern in gateway.patterns)
        for text in normalized
    ]

    gateway._semantic_scores(["Routine office procedure and ordinary document retention guidance."])
    semantic_scores = []
    started_semantic = time.perf_counter()
    for offset in range(0, len(rows), args.batch_size):
        batch_texts = [row["text"] for row in rows[offset:offset + args.batch_size]]
        semantic_scores.extend(gateway._semantic_scores(batch_texts))
    semantic_seconds = time.perf_counter() - started_semantic
    if len(semantic_scores) != len(rows):
        raise RuntimeError(f"Semantic score alignment failed: {len(semantic_scores)} vs {len(rows)}")

    # First verify live vLLM returns usable token log-probabilities. If not, the
    # run must fail rather than silently calibrate a semantic-only policy.
    warmup_ppl = gateway.perplexity("Routine office procedure and ordinary document retention guidance.")
    if warmup_ppl is None:
        raise RuntimeError("vLLM readiness endpoint returned no usable prompt-token log-probability score.")

    # Compute PPL once for every passage that may be eligible under any threshold
    # in the grid. The 0.00 minimum tests whether always-on PPL is safer/useful;
    # higher minimum-score values reduce calls only if their FPR/TPR trade-off wins.
    eligible_indices = [
        index for index, (score, marker_count) in enumerate(zip(semantic_scores, marker_counts))
        if marker_count < args.marker_threshold
        and (marker_count >= 1 or score >= min(PPL_MIN_CLASSIFIER_SCORES))
    ]
    ppl_scores: list[float | None] = [None] * len(rows)
    ppl_latencies_ms: list[float] = []

    def score_ppl(index: int):
        tick = time.perf_counter()
        value = gateway.perplexity(normalized[index])
        return index, value, (time.perf_counter() - tick) * 1000

    started_ppl = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.ppl_workers)) as executor:
        for index, value, latency in executor.map(score_ppl, eligible_indices):
            ppl_scores[index] = value
            ppl_latencies_ms.append(latency)
    ppl_seconds = time.perf_counter() - started_ppl
    observed_ppl_count = sum(ppl_scores[index] is not None for index in eligible_indices)

    records = []
    for min_score in PPL_MIN_CLASSIFIER_SCORES:
        for semantic_threshold in SEMANTIC_THRESHOLDS:
            for ppl_threshold in PPL_THRESHOLDS:
                records.append(summarize_operating_point(
                    rows,
                    semantic_scores,
                    marker_counts,
                    ppl_scores,
                    semantic_threshold,
                    ppl_threshold,
                    min_score,
                    args.marker_threshold,
                    True,
                ))
    decision = select_operating_point(records)
    result = {
        "schema_version": 1,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "validation_rows_path": str(args.validation_rows),
        "candidate_model_dir": str(args.model_dir),
        "model_id": ppl_model,
        "model_license": "Qwen/Qwen2.5-0.5B-Instruct Apache-2.0",
        "ppl_endpoint_configured": True,
        "sample_seed": args.seed,
        "source_calibration_license_notes": {
            "neuralchemy/Prompt-injection-dataset:full": "Apache-2.0",
            "geodesic-research/bipia/bipia": "CC-BY-SA-4.0",
            "bench-llm/or-bench:or-bench-80k train": "CC-BY-4.0",
            "Horizon-Labs/PIArena calibration slice": "MIT",
            "Horizon-Labs/NotInject calibration slice": "MIT",
        },
        "source_sample": sample_manifest,
        "marker_threshold": args.marker_threshold,
        "semantic_threshold_grid": list(SEMANTIC_THRESHOLDS),
        "ppl_threshold_grid": list(PPL_THRESHOLDS),
        "ppl_min_classifier_score_grid": list(PPL_MIN_CLASSIFIER_SCORES),
        "semantic_seconds": round(semantic_seconds, 3),
        "ppl_seconds": round(ppl_seconds, 3),
        "ppl_eligible_rows": len(eligible_indices),
        "ppl_observed_scores": observed_ppl_count,
        "ppl_score_coverage": round(observed_ppl_count / max(len(eligible_indices), 1), 6),
        "ppl_latency_ms": {
            "n": len(ppl_latencies_ms),
            "p50": round(float(statistics.median(ppl_latencies_ms)), 4) if ppl_latencies_ms else None,
            "p95": round(sorted(ppl_latencies_ms)[min(len(ppl_latencies_ms) - 1, int((len(ppl_latencies_ms) - 1) * 0.95 + 0.999999))], 4) if ppl_latencies_ms else None,
            "max": round(max(ppl_latencies_ms), 4) if ppl_latencies_ms else None,
        },
        **decision,
        "all_operating_points": records,
        "promotion_note": (
            "This report selects joint semantic + PPL thresholds only from the grouped training validation split. "
            "External OOD holdout rows are not loaded or used here. A feasible calibration is necessary but not sufficient; "
            "the fixed selected thresholds must still pass the untouched OOD acceptance workflow."
        ),
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "integrated_calibration.json"
    md_path = output_dir / "integrated_calibration.md"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    selected = result["selected_record"]
    lines = [
        "# Integrated semantic + vLLM PPL threshold calibration",
        "",
        f"- Completed UTC: {result['started_utc']}",
        f"- Candidate model: {args.model_dir}",
        f"- vLLM model: {ppl_model} (Apache-2.0)",
        f"- Sampled validation rows: {len(rows)}; seed={args.seed}",
        f"- PPL score coverage: {result['ppl_score_coverage']:.4f} ({observed_ppl_count}/{len(eligible_indices)} eligible rows)",
        f"- PPL latency p50/p95: {result['ppl_latency_ms']['p50']} / {result['ppl_latency_ms']['p95']} ms",
        f"- Selected semantic threshold: {result['selected_threshold']:.2f}",
        f"- Selected PPL threshold: {result['selected_ppl_threshold']:.2f}",
        f"- Selected min classifier score for PPL: {result['selected_min_classifier_score']:.2f}",
        f"- Feasible: {result['feasible']}; feasible grid points={result['feasible_point_count']}",
        f"- BIPIA validation TPR: {selected['bipia_injected_tpr']}",
        f"- Overall benign FPR: {selected['overall_benign']['fpr']}",
        f"- OR-Bench FPR: {selected['by_source']['orbench']['fpr']}",
        f"- NotInject FPR: {selected['by_source']['notinject']['fpr']}",
        f"- PIArena FPR: {selected['by_source']['piarena']['fpr']}",
        "",
        "| Source | N | TPR | FPR |",
        "|---|---:|---:|---:|",
    ]
    for group in SOURCES:
        m = selected["by_source"][group]
        lines.append(f"| {group} | {m['n']} | {m['tpr']} | {m['fpr']} |")
    lines += [
        "",
        "Selection constraints: overall benign FPR ≤5%, OR-Bench benign FPR ≤5%, NotInject benign FPR ≤5%, PIArena benign FPR ≤2%, minimum source sample counts satisfied.",
        "",
        result["selection_reason"],
        "",
        result["promotion_note"],
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "selected_threshold": result["selected_threshold"],
        "selected_ppl_threshold": result["selected_ppl_threshold"],
        "selected_min_classifier_score": result["selected_min_classifier_score"],
        "feasible": result["feasible"],
        "feasible_point_count": result["feasible_point_count"],
        "sample_counts": sample_manifest["critical_sample_counts"],
        "ppl_score_coverage": result["ppl_score_coverage"],
        "ppl_latency_ms": result["ppl_latency_ms"],
        "selected_record": result["selected_record"],
        "report": str(json_path),
    }, indent=2))
    if not result["feasible"]:
        # Produce a diagnostic artifact and fail the gating step immediately.
        # This prevents the later OOD evaluation from being mistaken for a
        # calibrated production candidate.
        raise SystemExit("No joint semantic/PPL threshold met validation FPR and sample-size gates.")


if __name__ == "__main__":
    main()

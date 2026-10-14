from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset, load_dataset
from sklearn.metrics import roc_auc_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments

BIPIA_DATASET = "geodesic-research/bipia"
EVAL_DATASET = "Horizon-Labs/prompt-injection-eval-suite"
BASE_MODEL = "Horizon-Labs/prompt-injection-guard-base"
MODEL_LICENSE = "Apache-2.0"
MAX_LENGTH = 512
WINDOW_OVERLAP = 64
DATASET_LICENSES = {
    "synthetic_v2_test": "Apache-2.0",
    "bipia": "CC-BY-SA-4.0",
    "piarena": "MIT",
    "notinject": "MIT",
    "orbench_hard": "CC-BY-4.0",
}


def remove_attack(text: str, attack: str) -> tuple[str, bool]:
    if not attack:
        return text, False
    pos = text.find(attack)
    if pos < 0:
        pos = text.lower().find(attack.lower())
    if pos < 0:
        return text, False
    clean = text[:pos] + " " + text[pos + len(attack):]
    clean = re.sub(r"[ \t]+\n", "\n", clean)
    clean = re.sub(r"\n[ \t]+", "\n", clean)
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean.strip(), True


def insert_attack(text: str, attack: str, position: str) -> str:
    position = (position or "end").lower()
    if position == "start":
        return attack + "\n" + text
    if position == "middle":
        index = len(text) // 2
        right = text.find(" ", index)
        left = text.rfind(" ", 0, index)
        choices = [i for i in (left, right) if i >= 0]
        if choices:
            index = min(choices, key=lambda i: abs(i - index))
        return text[:index] + "\n" + attack + "\n" + text[index:]
    return text + "\n" + attack


def digest_context(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def prepare_window(
    context: str,
    tokenizer,
    attack: str,
    position: str,
    is_poisoned: bool,
) -> dict:
    """Build matched-length clean/poisoned inputs and retain the insert location.

    Both labels start from the same clean context and receive an inserted span at
    the same start/middle/end position. The positive span is the source attack;
    the negative span is benign text tokenized to exactly the same number of
    tokens. This prevents a trivial inserted-span/length shortcut.
    """
    special_count = int(tokenizer.num_special_tokens_to_add(pair=False))
    content_limit = MAX_LENGTH - special_count
    context_ids = tokenizer.encode(context, add_special_tokens=False, truncation=False)
    attack_ids = tokenizer.encode(attack, add_special_tokens=False, truncation=False) if attack else []
    if not attack_ids:
        attack_ids = tokenizer.encode("ordinary context note", add_special_tokens=False, truncation=False)[:1]

    if is_poisoned:
        inserted_ids = attack_ids
    else:
        filler_ids = tokenizer.encode(
            "Ordinary background context information for this document. ",
            add_special_tokens=False,
            truncation=False,
        )
        if not filler_ids:
            filler_ids = [tokenizer.unk_token_id or tokenizer.eos_token_id or 0]
        repetitions = (len(attack_ids) + len(filler_ids) - 1) // len(filler_ids)
        inserted_ids = (filler_ids * repetitions)[:len(attack_ids)]

    normalized_position = (position or "end").lower()
    if normalized_position == "start":
        insert_at = 0
    elif normalized_position == "middle":
        insert_at = len(context_ids) // 2
    else:
        insert_at = len(context_ids)

    token_ids = context_ids[:insert_at] + inserted_ids + context_ids[insert_at:]
    inserted_start = insert_at
    inserted_end = inserted_start + len(inserted_ids)

    if len(token_ids) > content_limit:
        # Both classes have an equal-length inserted span and therefore choose
        # equivalent windows around that span for the same source context.
        wanted_start = inserted_start - max(0, (content_limit - len(inserted_ids)) // 2)
        start = min(max(0, wanted_start), len(token_ids) - content_limit)
        token_ids = token_ids[start:start + content_limit]

    encoded = tokenizer.prepare_for_model(
        token_ids,
        add_special_tokens=True,
        truncation=True,
        max_length=MAX_LENGTH,
        return_attention_mask=True,
    )
    return {
        key: value
        for key, value in encoded.items()
        if key in ("input_ids", "attention_mask", "token_type_ids")
    }


def load_bipia_pairs(cache_dir: str, max_rows: int, seed: int):
    source = load_dataset(BIPIA_DATASET, "bipia", split="train", cache_dir=cache_dir)
    rows = [
        dict(row) for row in source
        if str(row.get("context") or "").strip() and str(row.get("attack_str") or "").strip()
    ]
    random.Random(seed).shuffle(rows)
    if max_rows > 0:
        rows = rows[:max_rows]

    groups = defaultdict(list)
    matched = reconstructed = 0
    for row in rows:
        context = str(row["context"]).strip()
        attack = str(row["attack_str"]).strip()
        clean, found = remove_attack(context, attack)
        if found:
            poisoned = context
            matched += 1
        else:
            # Supports source rows that store the clean base context separately.
            clean = context
            poisoned = insert_attack(context, attack, str(row.get("position") or "end"))
            reconstructed += 1
        if len(clean) < 8:
            continue
        # Build the injected text at tokenization time from the same base context
        # used by the matched benign placeholder; both labels have equal span size.
        groups[digest_context(clean)].append((clean, attack, str(row.get("position") or "end"), str(row.get("id", ""))))

    group_ids = list(groups)
    random.Random(seed + 19).shuffle(group_ids)
    if len(group_ids) < 10:
        raise RuntimeError(f"Only {len(group_ids)} unique clean contexts found; insufficient for a grouped split")
    val_groups = set(group_ids[:max(1, int(len(group_ids) * 0.10))])
    train_examples, val_examples = [], []
    for group_id, variants in groups.items():
        target = val_examples if group_id in val_groups else train_examples
        for clean, attack, position, row_id in variants:
            target.append({"text": clean, "labels": 0, "attack": attack, "position": position, "group": group_id, "row_id": row_id})
            target.append({"text": clean, "labels": 1, "attack": attack, "position": position, "group": group_id, "row_id": row_id})
    info = {
        "dataset": f"{BIPIA_DATASET}/bipia",
        "license": "CC-BY-SA-4.0",
        "dataset_rows_available": len(source),
        "selected_source_rows": len(rows),
        "unique_clean_contexts": len(groups),
        "train_examples": len(train_examples),
        "validation_examples": len(val_examples),
        "source_context_already_contains_attack": matched,
        "attack_reconstructed_from_metadata": reconstructed,
        "matched_attack_ratio": round(matched / max(len(rows), 1), 6),
        "grouped_split_seed": seed + 19,
    }
    return train_examples, val_examples, info


def metrics(labels: list[int], scores: list[float], threshold: float) -> dict:
    predictions = [int(score >= threshold) for score in scores]
    tp = sum(y == 1 and p == 1 for y, p in zip(labels, predictions))
    tn = sum(y == 0 and p == 0 for y, p in zip(labels, predictions))
    fp = sum(y == 0 and p == 1 for y, p in zip(labels, predictions))
    fn = sum(y == 1 and p == 0 for y, p in zip(labels, predictions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    positives = sum(y == 1 for y in labels)
    negatives = sum(y == 0 for y in labels)
    try:
        auc = float(roc_auc_score(labels, scores)) if positives and negatives else None
    except ValueError:
        auc = None
    return {
        "n": len(labels), "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": round((tp + tn) / max(len(labels), 1), 6),
        "precision": round(precision, 6), "recall_tpr": round(recall, 6),
        "fpr": round(fp / negatives, 6) if negatives else None,
        "f1": round(f1, 6), "roc_auc": round(auc, 6) if auc is not None else None,
    }


def sample_config(rows: list[dict], max_per_class: int, seed: int, benign_only_ok: bool) -> list[dict]:
    pools = {0: [], 1: []}
    for row in rows:
        try:
            label, text = int(row["label"]), str(row["text"]).strip()
        except (KeyError, ValueError, TypeError):
            continue
        if label in pools and text:
            pools[label].append({"label": label, "text": text, "kind": row.get("kind")})
    rng = random.Random(seed)
    if not pools[1] or not pools[0]:
        if not benign_only_ok:
            raise RuntimeError("Expected both labels for this benchmark config")
        pool = pools[0] or pools[1]
        return rng.sample(pool, min(len(pool), max_per_class))
    count = min(max_per_class, len(pools[0]), len(pools[1]))
    chosen = rng.sample(pools[0], count) + rng.sample(pools[1], count)
    rng.shuffle(chosen)
    return chosen


def external_evaluation(model_dir: Path, cache_dir: str, max_per_class: int, seed: int) -> dict:
    from enterprise_graphrag.security import SecurityGateway

    gateway = SecurityGateway(
        classifier_model=str(model_dir),
        classifier_threshold=0.5,
        classifier_max_length=MAX_LENGTH,
        classifier_device="cuda" if torch.cuda.is_available() else "cpu",
        classifier_window_overlap=WINDOW_OVERLAP,
        marker_threshold=1_000_000,
    )

    def score_texts(texts: list[str]) -> tuple[list[float], float]:
        if not texts:
            return [], 0.0
        gateway._semantic_scores(["Routine office policy and records management guidance."])
        started = time.perf_counter()
        values = []
        for offset in range(0, len(texts), 16):
            values.extend(gateway._semantic_scores(texts[offset:offset + 16]))
        return values, time.perf_counter() - started

    def score_quantiles(scores: list[float]) -> dict:
        if not scores:
            return {}
        return {
            "min": round(float(np.min(scores)), 8),
            "p50": round(float(np.percentile(scores, 50)), 8),
            "p90": round(float(np.percentile(scores, 90)), 8),
            "p95": round(float(np.percentile(scores, 95)), 8),
            "p99": round(float(np.percentile(scores, 99)), 8),
            "max": round(float(np.max(scores)), 8),
        }

    evaluation_rows = {}
    calibration_scores = []
    calibration_meta = {}
    for config in ("synthetic_v2_test", "bipia", "piarena", "notinject", "orbench_hard"):
        ds = load_dataset(EVAL_DATASET, config, split="test", cache_dir=cache_dir)
        benign_only = config in ("notinject", "orbench_hard")
        sample_count = max_per_class * 2 if benign_only else max_per_class
        picked = sample_config(
            [dict(row) for row in ds],
            sample_count,
            seed + len(evaluation_rows) * 11,
            benign_only_ok=benign_only,
        )
        if benign_only:
            calibration_rows = picked[:max_per_class]
            test_rows = picked[max_per_class:]
            calibration_texts = [str(row["text"]) for row in calibration_rows]
            calibration_scores_for_config, calibration_seconds = score_texts(calibration_texts)
            calibration_scores.extend(calibration_scores_for_config)
            calibration_meta[config] = {
                "license": DATASET_LICENSES[config],
                "rows": len(calibration_rows),
                "score_quantiles": score_quantiles(calibration_scores_for_config),
                "runtime_seconds": round(calibration_seconds, 4),
            }
        else:
            test_rows = picked

        texts = [str(row["text"]) for row in test_rows]
        labels = [int(row["label"]) for row in test_rows]
        scores, duration = score_texts(texts)
        latency = []
        for text in texts[:min(50, len(texts))]:
            started = time.perf_counter()
            gateway._semantic_scores([text])
            latency.append((time.perf_counter() - started) * 1000)
        evaluation_rows[config] = {
            "dataset_rows": len(ds),
            "license": DATASET_LICENSES[config],
            "labels": labels,
            "scores": scores,
            "sample": {
                "benign": sum(label == 0 for label in labels),
                "injected": sum(label == 1 for label in labels),
                "seed": seed + len(evaluation_rows) * 11,
                "holdout_of_benign_threshold_calibration": benign_only,
            },
            "inference": {
                "device": "cuda" if torch.cuda.is_available() else "cpu",
                "elapsed_seconds": round(duration, 4),
                "rows_per_second": round(len(texts) / max(duration, 1e-9), 3),
                "latency_p50_ms": round(float(np.percentile(latency, 50)), 4) if latency else None,
                "latency_p95_ms": round(float(np.percentile(latency, 95)), 4) if latency else None,
            },
        }

    # Select the lowest threshold whose FPR is <=5% on the calibration halves of
    # NotInject and OR-Bench-hard. Their remaining halves are withheld for testing.
    target_fpr = 0.05
    calibrated_threshold = None
    calibration_fpr = None
    if calibration_scores:
        feasible = [
            threshold for threshold in sorted(set(float(x) for x in calibration_scores))
            if sum(score >= threshold for score in calibration_scores) / len(calibration_scores) <= target_fpr
        ]
        if feasible:
            calibrated_threshold = min(feasible)
            calibration_fpr = sum(score >= calibrated_threshold for score in calibration_scores) / len(calibration_scores)

    thresholds = (
        0.10, 0.20, 0.35, 0.50, 0.65, 0.80, 0.90,
        0.95, 0.97, 0.98, 0.99, 0.995, 0.999, 0.9995, 0.9999, 0.99999,
    )
    results = {}
    for config, row in evaluation_rows.items():
        labels, scores = row["labels"], row["scores"]
        threshold_sweep = {
            f"{threshold:.5f}": metrics(labels, scores, threshold)
            for threshold in thresholds
        }
        calibrated_metrics = (
            metrics(labels, scores, calibrated_threshold)
            if calibrated_threshold is not None
            else None
        )
        results[config] = {
            "dataset_rows": row["dataset_rows"],
            "license": row["license"],
            "sample": row["sample"],
            "threshold_sweep": threshold_sweep,
            "score_quantiles": {
                "benign": score_quantiles([score for label, score in zip(labels, scores) if label == 0]),
                "injected": score_quantiles([score for label, score in zip(labels, scores) if label == 1]),
            },
            "calibrated_threshold_metrics": calibrated_metrics,
            "inference": row["inference"],
        }

    for config, meta in calibration_meta.items():
        meta["calibrated_threshold"] = calibrated_threshold
        meta["observed_calibration_fpr"] = calibration_fpr
    return {
        "calibration": {
            "method": "lowest observed score threshold with <=5% FPR on the calibration halves of NotInject + OR-Bench-hard",
            "target_fpr": target_fpr,
            "examples": len(calibration_scores),
            "threshold": calibrated_threshold,
            "observed_calibration_fpr": calibration_fpr,
            "datasets": calibration_meta,
            "warning": "Threshold selection uses only calibration halves of benign-only datasets. Use the other halves and injected datasets as evaluation; calibration FPR is not an independent test result.",
        },
        "configs": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Fine-tune a licensed DeBERTa classifier on BIPIA and evaluate external generalization.")
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "graphrag-bipia-training"))
    parser.add_argument("--output-dir", default="artifacts/bipia-finetuned-guard")
    parser.add_argument("--model-dir", default="artifacts/bipia-finetuned-guard/model")
    parser.add_argument("--base-model", default=BASE_MODEL)
    parser.add_argument("--max-train-rows", type=int, default=8000)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--learning-rate", type=float, default=1e-6)
    parser.add_argument("--train-batch-size", type=int, default=16)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=2)
    parser.add_argument("--eval-max-per-class", type=int, default=100)
    parser.add_argument("--seed", type=int, default=20261012)
    args = parser.parse_args()
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    output_dir = Path(args.output_dir)
    model_dir = Path(args.model_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = str(Path(args.cache_dir))
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    started_utc = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()

    # Capture a same-sample baseline before adaptation; do not select a candidate
    # on training/validation loss alone.
    baseline_eval = external_evaluation(args.base_model, cache_dir, args.eval_max_per_class, args.seed)

    train_rows, val_rows, train_info = load_bipia_pairs(cache_dir, args.max_train_rows, args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=False)

    def tokenize_batch(batch):
        encoded_rows = [
            prepare_window(text, tokenizer, attack, position, int(label) == 1)
            for text, attack, position, label in zip(batch["text"], batch["attack"], batch["position"], batch["labels"])
        ]
        features = {
            key: [row[key] for row in encoded_rows]
            for key in encoded_rows[0]
        }
        features["labels"] = [int(value) for value in batch["labels"]]
        return features

    train_raw = Dataset.from_list(train_rows)
    val_raw = Dataset.from_list(val_rows)
    train_ds = train_raw.map(tokenize_batch, batched=True, remove_columns=train_raw.column_names, desc="Tokenizing BIPIA training examples")
    val_ds = val_raw.map(tokenize_batch, batched=True, remove_columns=val_raw.column_names, desc="Tokenizing BIPIA validation examples")

    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        num_labels=2,
        id2label={0: "LEGIT", 1: "INJECTION"},
        label2id={"LEGIT": 0, "INJECTION": 1},
    )
    model.config.id2label = {0: "LEGIT", 1: "INJECTION"}
    model.config.label2id = {"LEGIT": 0, "INJECTION": 1}
    on_gpu = torch.cuda.is_available()
    if on_gpu:
        torch.backends.cuda.matmul.allow_tf32 = True
    training_args = TrainingArguments(
        output_dir=str(output_dir / "trainer"),
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_ratio=0.06,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=100,
        fp16=on_gpu,
        report_to=[],
        seed=args.seed,
        data_seed=args.seed,
        dataloader_num_workers=4,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        processing_class=tokenizer,
    )
    training = trainer.train()
    validation = trainer.evaluate()
    trainer.save_model(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))
    external = external_evaluation(model_dir, cache_dir, args.eval_max_per_class, args.seed)

    base_bipia = baseline_eval["configs"]["bipia"]["calibrated_threshold_metrics"] or {}
    base_piarena = baseline_eval["configs"]["piarena"]["calibrated_threshold_metrics"] or {}
    tuned_bipia = external["configs"]["bipia"]["calibrated_threshold_metrics"] or {}
    tuned_piarena = external["configs"]["piarena"]["calibrated_threshold_metrics"] or {}
    tuned_notinject = external["configs"]["notinject"]["calibrated_threshold_metrics"] or {}
    tuned_orbench = external["configs"]["orbench_hard"]["calibrated_threshold_metrics"] or {}
    benign_fprs = [m.get("fpr") for m in (tuned_notinject, tuned_orbench) if m.get("fpr") is not None]
    benign_fpr_ok = len(benign_fprs) == 2 and all(value <= 0.05 for value in benign_fprs)
    bipia_improved = tuned_bipia.get("recall_tpr", 0.0) >= base_bipia.get("recall_tpr", 0.0) + 0.05
    piarena_preserved = tuned_piarena.get("recall_tpr", 0.0) >= base_piarena.get("recall_tpr", 0.0) - 0.02
    selected_finetuned = bool(benign_fpr_ok and bipia_improved and piarena_preserved)
    recommended_default = str(model_dir) if selected_finetuned else args.base_model

    result = {
        "schema_version": 1,
        "started_utc": started_utc,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - start_time, 3),
        "seed": args.seed,
        "base_model": args.base_model,
        "base_model_license": MODEL_LICENSE,
        "checkpoint_dir": str(model_dir),
        "training_dataset": train_info,
        "training_dataset_license": "CC-BY-SA-4.0",
        "window_alignment": "clean and poisoned samples use corresponding insertion-position windows; poisoned windows are centered on detected attack span when possible",
        "training_config": {
            "epochs": args.epochs,
            "train_batch_size": args.train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "learning_rate": args.learning_rate,
            "max_sequence_length": MAX_LENGTH,
            "window_overlap": WINDOW_OVERLAP,
        },
        "training_metrics": training.metrics,
        "validation_metrics": validation,
        "baseline_eval": baseline_eval,
        "external_eval": external,
        "candidate_selection": {
            "selected_finetuned_checkpoint": selected_finetuned,
            "recommended_default_model": recommended_default,
            "benign_fpr_ok": benign_fpr_ok,
            "bipia_improved_by_5_points": bipia_improved,
            "piarena_preserved_within_2_points": piarena_preserved,
            "rule": "Only select fine-tuned candidate if calibrated held-out FPR <=5% on both NotInject and OR-Bench-hard, BIPIA TPR improves >=5 points, and PIArena TPR degrades by no more than 2 points.",
            "baseline_calibrated": {"bipia": base_bipia, "piarena": base_piarena},
            "finetuned_calibrated": {
                "bipia": tuned_bipia,
                "piarena": tuned_piarena,
                "notinject": tuned_notinject,
                "orbench_hard": tuned_orbench,
            },
        },
        "note": (
            "BIPIA source contexts and attack strings may overlap conceptually with the BIPIA benchmark family. "
            "Treat BIPIA results as in-family diagnostics; prioritize PIArena and benign hard-negative results for generalization. "
            "Training uses CC-BY-SA-4.0 data; preserve attribution and obtain legal review before redistributing weights."
        ),
    }
    (output_dir / "training_and_evaluation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    cal = external["calibration"]
    eval_configs = external["configs"]
    lines = [
        "# BIPIA-finetuned injection classifier",
        "",
        f"- Started UTC: {result['started_utc']}",
        f"- Completed UTC: {result['completed_utc']}",
        f"- Runtime: {result['elapsed_seconds']} seconds",
        f"- Base model: {args.base_model} (MIT)",
        f"- Training source: {BIPIA_DATASET}/bipia (CC-BY-SA-4.0)",
        f"- Selected source rows: {train_info['selected_source_rows']} / {train_info['dataset_rows_available']}",
        f"- Unique contexts: {train_info['unique_clean_contexts']}; training pairs: {train_info['train_examples']}; validation pairs: {train_info['validation_examples']}",
        f"- Context attack-match ratio: {train_info['matched_attack_ratio']:.4f}; reconstructed rows: {train_info['attack_reconstructed_from_metadata']}",
        f"- Epochs: {args.epochs}; sequence length: {MAX_LENGTH}; device: {'CUDA' if on_gpu else 'CPU'}",
        f"- Calibrated threshold: {cal['threshold']}; target benign FPR={cal['target_fpr']}; observed calibration FPR={cal['observed_calibration_fpr']}",
        "- Calibration data: one half each of NotInject + OR-Bench-hard; reported metrics use the remaining halves for those two datasets.",
        "",
        "| Config | License | N | ROC-AUC | TPR @ .50 | FPR @ .50 | TPR @ calibrated | FPR @ calibrated | F1 @ calibrated |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for config, value in eval_configs.items():
        m50 = value["threshold_sweep"]["0.50000"]
        mc = value["calibrated_threshold_metrics"]
        lines.append(
            f"| {config} | {value['license']} | {m50['n']} | {m50['roc_auc']} | "
            f"{m50['recall_tpr']:.4f} | {m50['fpr'] if m50['fpr'] is not None else 'n/a'} | "
            f"{mc['recall_tpr'] if mc else 'n/a'} | {mc['fpr'] if mc else 'n/a'} | "
            f"{mc['f1'] if mc else 'n/a'} |"
        )
    lines += ["", "## Score distributions", ""]
    for config, value in eval_configs.items():
        lines.append(f"- {config} benign score quantiles: {value['score_quantiles']['benign']}")
        lines.append(f"- {config} injected score quantiles: {value['score_quantiles']['injected']}")
    lines += [
        "",
        "## License and interpretation notes",
        "",
        "- Base checkpoint microsoft/deberta-v3-base: MIT.",
        "- BIPIA training source geodesic-research/bipia: CC-BY-SA-4.0; preserve attribution/share-alike terms for redistributed derived material.",
        "- Evaluation config licenses: synthetic_v2_test Apache-2.0, BIPIA CC-BY-SA-4.0, PIArena MIT, NotInject MIT, OR-Bench-hard CC-BY-4.0.",
        "- BIPIA results are in-family diagnostics; use PIArena and benign hard-negative results as the main generalization checks.",
        "- Threshold results are fixed-seed sample estimates and do not guarantee universal injection detection.",
        "",
        result["note"],
    ]
    (output_dir / "training_and_evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

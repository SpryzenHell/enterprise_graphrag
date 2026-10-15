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

import torch
from datasets import Dataset, load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

BIPIA_DATASET = "geodesic-research/bipia"
MIXED_DATASET = "neuralchemy/Prompt-injection-dataset"
OR_BENCH_DATASET = "bench-llm/or-bench"
OOD_EVAL_DATASET = "Horizon-Labs/prompt-injection-eval-suite"
BASE_MODEL = "Horizon-Labs/prompt-injection-guard-base"
OR_BENCH_LICENSE = "CC-BY-4.0"


def normalized_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text).strip().casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def parse_label(value) -> int | None:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)) and int(value) in (0, 1):
        return int(value)
    text = str(value).strip().casefold()
    if text in {"0", "benign", "safe", "legit", "legitimate", "non-injection", "non_injection"}:
        return 0
    if text in {"1", "malicious", "attack", "injection", "prompt_injection", "prompt-injection"}:
        return 1
    return None


def remove_attack(text: str, attack: str) -> tuple[str, bool]:
    if not attack:
        return text, False
    pos = text.find(attack)
    if pos < 0:
        pos = text.casefold().find(attack.casefold())
    if pos < 0:
        return text, False
    clean = text[:pos] + " " + text[pos + len(attack):]
    clean = re.sub(r"[ \t]+\n", "\n", clean)
    clean = re.sub(r"\n[ \t]+", "\n", clean)
    clean = re.sub(r"\n{3,}", "\n\n", clean)
    return clean.strip(), True


def insert_attack(text: str, attack: str, position: str) -> str:
    pos = (position or "end").casefold()
    if pos == "start":
        return attack + "\n" + text
    if pos == "middle":
        middle = len(text) // 2
        left = text.rfind(" ", 0, middle)
        right = text.find(" ", middle)
        boundaries = [x for x in (left, right) if x >= 0]
        if boundaries:
            middle = min(boundaries, key=lambda x: abs(x - middle))
        return text[:middle] + "\n" + attack + "\n" + text[middle:]
    return text + "\n" + attack


def split_notinject_rows(rows, seed: int, train_fraction: float, validation_fraction: float):
    """Partition benign NotInject examples into train, threshold-calibration and untouched holdout."""
    if not 0.0 < train_fraction < 1.0 or not 0.0 < validation_fraction < 1.0:
        raise ValueError("NotInject train/validation fractions must be between 0 and 1")
    if train_fraction + validation_fraction >= 1.0:
        raise ValueError("NotInject train + validation fractions must leave a non-empty holdout")

    unique = {}
    for row in rows:
        text = str(row.get("text") or "").strip()
        label = parse_label(row.get("label", 0))
        if len(text) < 8 or label != 0:
            continue
        unique.setdefault(normalized_hash(text), {
            "text": text,
            "label": 0,
            "attack": "",
            "position": "end",
            "source": "leolee99/NotInject",
        })
    items = list(unique.items())
    random.Random(seed).shuffle(items)
    if len(items) < 50:
        raise RuntimeError(f"Only {len(items)} unique benign NotInject rows; expected at least 50")
    train_end = max(1, int(len(items) * train_fraction))
    validation_end = max(train_end + 1, int(len(items) * (train_fraction + validation_fraction)))
    validation_end = min(validation_end, len(items) - 1)
    train_items = items[:train_end]
    validation_items = items[train_end:validation_end]
    holdout_items = items[validation_end:]
    manifest = {
        "dataset": "Horizon-Labs/prompt-injection-eval-suite/notinject",
        "upstream_dataset": "leolee99/NotInject",
        "license": "MIT",
        "seed": seed,
        "source_rows": len(rows),
        "unique_rows": len(items),
        "train_rows": len(train_items),
        "validation_rows": len(validation_items),
        "holdout_rows": len(holdout_items),
        "training_hashes": sorted(key for key, _ in train_items),
        "validation_hashes": sorted(key for key, _ in validation_items),
        "holdout_hashes": sorted(key for key, _ in holdout_items),
        "excluded_hashes": sorted(key for key, _ in train_items + validation_items),
        "split_policy": "exact normalized text-hash split; only the untouched holdout partition is scored as NotInject",
    }
    return (
        [row for _, row in train_items],
        [row for _, row in validation_items],
        [row for _, row in holdout_items],
        manifest,
    )


def split_labeled_validation_rows(rows, seed: int, validation_fraction: float = 0.20):
    """Reserve a stratified calibration slice from the PIArena config without training on it."""
    if not 0.0 < validation_fraction < 0.5:
        raise ValueError("PIArena validation fraction must be between 0 and 0.5")
    pools = {0: {}, 1: {}}
    for row in rows:
        text = str(row.get("text") or "").strip()
        label = parse_label(row.get("label"))
        if len(text) >= 8 and label in (0, 1):
            pools[label].setdefault(normalized_hash(text), {
                "text": text,
                "label": label,
                "attack": "",
                "position": "end",
                "source": "Horizon-Labs/PIArena",
            })
    if not pools[0] or not pools[1]:
        raise RuntimeError("PIArena partition requires both benign and injected rows")
    rng = random.Random(seed)
    validation_rows = []
    holdout_rows = []
    validation_hashes = []
    holdout_hashes = []
    for label in (0, 1):
        items = list(pools[label].items())
        rng.shuffle(items)
        val_count = max(1, int(len(items) * validation_fraction))
        validation_items, holdout_items = items[:val_count], items[val_count:]
        validation_rows.extend(row for _, row in validation_items)
        holdout_rows.extend(row for _, row in holdout_items)
        validation_hashes.extend(key for key, _ in validation_items)
        holdout_hashes.extend(key for key, _ in holdout_items)
    manifest = {
        "dataset": "Horizon-Labs/prompt-injection-eval-suite/piarena",
        "license": "MIT",
        "seed": seed,
        "validation_fraction_per_class": validation_fraction,
        "validation_rows": len(validation_rows),
        "holdout_rows": len(holdout_rows),
        "validation_hashes": sorted(validation_hashes),
        "holdout_hashes": sorted(holdout_hashes),
        "excluded_hashes": sorted(validation_hashes),
        "split_policy": "stratified normalized-text-hash calibration slice; remaining examples are the untouched PIArena holdout",
    }
    return validation_rows, holdout_rows, manifest


def load_mixed_rows(
    cache_dir: str,
    max_bipia_rows: int,
    max_orbench_rows: int,
    seed: int,
    notinject_train_fraction: float,
    notinject_validation_fraction: float,
    notinject_oversample_factor: int,
):
    rng = random.Random(seed)
    grouped: dict[str, list[dict]] = defaultdict(list)
    raw_counts = {
        "mixed_dataset_rows": 0,
        "mixed_dataset_usable": 0,
        "mixed_rows_excluded_notinject_overlap": 0,
        "bipia_dataset_rows": 0,
        "bipia_selected_rows": 0,
        "bipia_pairs": 0,
        "bipia_existing_attack_matches": 0,
        "bipia_reconstructed_attacks": 0,
        "orbench_source_rows": 0,
        "orbench_rows_added": 0,
        "orbench_rows_excluded_heldout_overlap": 0,
        "orbench_rows_excluded_duplicate": 0,
        "notinject_rows_added_to_training": 0,
        "notinject_rows_added_to_validation": 0,
        "notinject_rows_excluded_duplicate": 0,
        "mixed_rows_excluded_ood_calibration_overlap": 0,
        "piarena_rows_added_to_calibration": 0,
        "piarena_rows_excluded_duplicate": 0,
    }
    if notinject_oversample_factor < 1:
        raise ValueError("notinject_oversample_factor must be at least 1")

    # Build a fixed group-aware split for the 339-row benign-only NotInject pool.
    # Its training/calibration hashes are excluded from the later final evaluation.
    notinject_source = load_dataset(
        OOD_EVAL_DATASET,
        "notinject",
        split="test",
        cache_dir=cache_dir,
    )
    notinject_train, notinject_validation, notinject_holdout, notinject_manifest = split_notinject_rows(
        [dict(row) for row in notinject_source],
        seed=seed + 73,
        train_fraction=notinject_train_fraction,
        validation_fraction=notinject_validation_fraction,
    )
    notinject_all_hashes = (
        set(notinject_manifest["training_hashes"])
        | set(notinject_manifest["validation_hashes"])
        | set(notinject_manifest["holdout_hashes"])
    )

    # Reserve a calibration-only PIArena slice. Remaining PIArena rows are untouched
    # holdout rows; no PIArena example is used as a gradient-training example.
    piarena_source = load_dataset(
        OOD_EVAL_DATASET,
        "piarena",
        split="test",
        cache_dir=cache_dir,
    )
    piarena_validation, piarena_holdout, piarena_manifest = split_labeled_validation_rows(
        [dict(row) for row in piarena_source],
        seed=seed + 79,
        validation_fraction=0.20,
    )
    piarena_all_hashes = {
        normalized_hash(str(row.get("text") or ""))
        for row in piarena_source
        if len(str(row.get("text") or "").strip()) >= 8
    }
    ood_eval_hashes = notinject_all_hashes | piarena_all_hashes

    # Preserve group_id so augmented variants cannot leak across training/validation.
    mixed = load_dataset(MIXED_DATASET, "full", split="train", cache_dir=cache_dir)
    raw_counts["mixed_dataset_rows"] = len(mixed)
    for row in mixed:
        text = str(row.get("text") or row.get("prompt") or "").strip()
        label = parse_label(row.get("label"))
        if len(text) < 8 or label is None:
            continue
        if normalized_hash(text) in ood_eval_hashes:
            raw_counts["mixed_rows_excluded_ood_calibration_overlap"] += 1
            continue
        raw_group_id = row.get("group_id")
        group_id = str(raw_group_id).strip() if raw_group_id is not None else ""
        if not group_id or group_id.casefold() in {"nan", "none", "null"}:
            group_id = normalized_hash(text)
        grouped["mixed:" + group_id].append({
            "text": text,
            "label": label,
            "attack": "",
            "position": "end",
            "source": "neuralchemy/Prompt-injection-dataset:full",
            "group_id": "mixed:" + group_id,
        })
        raw_counts["mixed_dataset_usable"] += 1

    bipia = load_dataset(BIPIA_DATASET, "bipia", split="train", cache_dir=cache_dir)
    raw_counts["bipia_dataset_rows"] = len(bipia)
    rows = [
        dict(row) for row in bipia
        if str(row.get("context") or "").strip() and str(row.get("attack_str") or "").strip()
    ]
    rng.shuffle(rows)
    if max_bipia_rows > 0:
        rows = rows[:max_bipia_rows]
    raw_counts["bipia_selected_rows"] = len(rows)

    for row in rows:
        context = str(row["context"]).strip()
        attack = str(row["attack_str"]).strip()
        position = str(row.get("position") or "end")
        clean, found = remove_attack(context, attack)
        if found:
            poisoned = context
            raw_counts["bipia_existing_attack_matches"] += 1
        else:
            clean = context
            poisoned = insert_attack(context, attack, position)
            raw_counts["bipia_reconstructed_attacks"] += 1
        if len(clean) < 8 or len(poisoned) < 8:
            continue
        group_id = "bipia:" + normalized_hash(clean)
        grouped[group_id].append({
            "text": clean,
            "label": 0,
            "attack": attack,
            "position": position,
            "source": "geodesic-research/bipia/bipia-clean-pair",
            "group_id": group_id,
        })
        grouped[group_id].append({
            "text": poisoned,
            "label": 1,
            "attack": attack,
            "position": position,
            "source": "geodesic-research/bipia/bipia-injected-pair",
            "group_id": group_id,
        })
        raw_counts["bipia_pairs"] += 1

    # Decontaminate OR-Bench training against the entire NotInject split and the
    # official OR-Bench-hard holdout. No held-out string enters the train pool.
    heldout_eval_hashes = set(ood_eval_hashes)
    heldout_eval_rows = len(ood_eval_hashes)
    orbench_hard = load_dataset(
        OOD_EVAL_DATASET,
        "orbench_hard",
        split="test",
        cache_dir=cache_dir,
    )
    for heldout_row in orbench_hard:
        heldout_text = str(heldout_row.get("text") or "").strip()
        if len(heldout_text) >= 8:
            heldout_eval_hashes.add(normalized_hash(heldout_text))
            heldout_eval_rows += 1

    orbench = load_dataset(
        OR_BENCH_DATASET,
        "or-bench-80k",
        split="train",
        cache_dir=cache_dir,
    )
    raw_counts["orbench_source_rows"] = len(orbench)
    used_hashes = {
        normalized_hash(example["text"])
        for examples in grouped.values()
        for example in examples
    }
    hard_negative_rows = []
    for row in orbench:
        text = str(row.get("prompt") or row.get("text") or "").strip()
        if len(text) < 8:
            continue
        text_hash = normalized_hash(text)
        if text_hash in heldout_eval_hashes:
            raw_counts["orbench_rows_excluded_heldout_overlap"] += 1
            continue
        if text_hash in used_hashes:
            raw_counts["orbench_rows_excluded_duplicate"] += 1
            continue
        hard_negative_rows.append((text_hash, text))
    rng.shuffle(hard_negative_rows)
    if max_orbench_rows > 0:
        hard_negative_rows = hard_negative_rows[:max_orbench_rows]

    for text_hash, text in hard_negative_rows:
        group_id = "orbench80k:" + text_hash
        grouped[group_id].append({
            "text": text,
            "label": 0,
            "attack": "",
            "position": "end",
            "source": "bench-llm/or-bench:or-bench-80k-train",
            "group_id": group_id,
        })
        raw_counts["orbench_rows_added"] += 1
        used_hashes.add(text_hash)

    if len(grouped) < 20:
        raise RuntimeError(f"Insufficient distinct groups for leak-resistant split: {len(grouped)}")

    group_ids = list(grouped)
    rng.shuffle(group_ids)
    validation_groups = set(group_ids[:max(1, round(len(group_ids) * 0.10))])
    train_rows, validation_rows = [], []
    for group_id, examples in grouped.items():
        destination = validation_rows if group_id in validation_groups else train_rows
        destination.extend(examples)

    train_text_hashes = {normalized_hash(row["text"]) for row in train_rows}
    before_val = len(validation_rows)
    validation_rows = [
        row for row in validation_rows
        if normalized_hash(row["text"]) not in train_text_hashes
    ]
    removed_cross_source_overlap = before_val - len(validation_rows)
    if not train_rows or not validation_rows:
        raise RuntimeError("Leak-resistant grouped split produced an empty partition")

    # Add only the disjoint NotInject training slice and validation slice after the
    # multi-source split. A fixed oversampling factor counteracts its smaller size.
    grouped_corpus_hashes = {
        normalized_hash(row["text"])
        for examples in grouped.values()
        for row in examples
    }
    usable_piarena_validation = [
        row for row in piarena_validation
        if normalized_hash(row["text"]) not in grouped_corpus_hashes
        and normalized_hash(row["text"]) not in notinject_all_hashes
    ]
    raw_counts["piarena_rows_excluded_duplicate"] = (
        len(piarena_validation) - len(usable_piarena_validation)
    )
    validation_rows.extend(
        {
            **row,
            "group_id": "piarena-validation:" + normalized_hash(row["text"]),
            "source": "Horizon-Labs/PIArena:validation",
        }
        for row in usable_piarena_validation
    )
    raw_counts["piarena_rows_added_to_calibration"] = len(usable_piarena_validation)

    usable_notinject_train = [
        row for row in notinject_train
        if normalized_hash(row["text"]) not in grouped_corpus_hashes
    ]
    usable_notinject_validation = [
        row for row in notinject_validation
        if normalized_hash(row["text"]) not in grouped_corpus_hashes
    ]
    raw_counts["notinject_rows_excluded_duplicate"] = (
        len(notinject_train) - len(usable_notinject_train)
        + len(notinject_validation) - len(usable_notinject_validation)
    )
    notinject_train_examples = [
        {
            **row,
            "group_id": "notinject-train:" + normalized_hash(row["text"]),
            "source": "leolee99/NotInject:train",
        }
        for row in usable_notinject_train
    ]
    train_rows.extend(notinject_train_examples * notinject_oversample_factor)
    validation_rows.extend(
        {
            **row,
            "group_id": "notinject-validation:" + normalized_hash(row["text"]),
            "source": "leolee99/NotInject:validation",
        }
        for row in usable_notinject_validation
    )
    raw_counts["notinject_rows_added_to_training"] = len(usable_notinject_train) * notinject_oversample_factor
    raw_counts["notinject_rows_added_to_validation"] = len(usable_notinject_validation)

    train_counts = {
        "benign": sum(row["label"] == 0 for row in train_rows),
        "injected": sum(row["label"] == 1 for row in train_rows),
    }
    validation_counts = {
        "benign": sum(row["label"] == 0 for row in validation_rows),
        "injected": sum(row["label"] == 1 for row in validation_rows),
    }
    if min(train_counts.values()) == 0 or min(validation_counts.values()) == 0:
        raise RuntimeError(
            f"Training and validation must both contain both classes: train={train_counts}, val={validation_counts}"
        )

    notinject_manifest["train_rows_added_to_model"] = len(usable_notinject_train)
    notinject_manifest["validation_rows_added_to_calibration"] = len(usable_notinject_validation)
    notinject_manifest["oversample_factor"] = notinject_oversample_factor
    notinject_manifest["excluded_by_exact_overlap"] = raw_counts["notinject_rows_excluded_duplicate"]
    notinject_manifest["excluded_hashes_by_config"] = {
        "notinject": list(notinject_manifest["excluded_hashes"]),
        "piarena": list(piarena_manifest["excluded_hashes"]),
    }
    notinject_manifest["config_partitions"] = {
        "notinject": notinject_manifest,
        "piarena": piarena_manifest,
    }
    notinject_manifest["holdout_policy"] = (
        "NotInject scores untouched 25% holdout; PIArena scores rows outside the calibration-only 20% stratified slice."
    )

    return train_rows, validation_rows, {
        **raw_counts,
        "distinct_groups": len(grouped),
        "train_examples": len(train_rows),
        "validation_examples": len(validation_rows),
        "train_class_counts": train_counts,
        "validation_class_counts": validation_counts,
        "context_grouped_split_seed": seed,
        "removed_exact_text_overlaps_from_validation": removed_cross_source_overlap,
        "notinject_split": {
            "train_rows": len(usable_notinject_train),
            "oversampled_training_examples": len(usable_notinject_train) * notinject_oversample_factor,
            "validation_rows": len(usable_notinject_validation),
            "holdout_rows": len(notinject_holdout),
            "piarena_calibration_rows": len(usable_piarena_validation),
            "piarena_holdout_rows": len(piarena_holdout),
            "holdout_policy": "only untouched NotInject holdout and PIArena rows excluding the calibration slice are evaluated",
        },
        "license_notes": {
            "neuralchemy/Prompt-injection-dataset:full": "Apache-2.0 dataset card; group_id preserved for augmented variants",
            "geodesic-research/bipia/bipia": "CC-BY-SA-4.0; retain attribution and share-alike notice for redistributed derivative weights",
            "bench-llm/or-bench:or-bench-80k train": "CC-BY-4.0; use only the train split and exclude exact evaluation text overlap",
            "Horizon-Labs/prompt-injection-eval-suite/notinject": "MIT; partitioned by normalized text hash into train, calibration validation, and untouched test holdout",
            "Horizon-Labs/prompt-injection-eval-suite/piarena": "MIT; stratified 20% calibration split, remaining rows reserved for untouched evaluation",
            "held-out benchmark decontamination": f"Hashed {heldout_eval_rows} NotInject/OR-Bench-hard rows; exact overlaps excluded from OR-Bench training",
            "base_model": "Horizon-Labs/prompt-injection-guard-base (Apache-2.0 per model card)",
        },
    }, notinject_manifest

def prepare_training_window(
    text: str,
    tokenizer,
    attack: str,
    position: str,
    is_poisoned: bool,
    max_length: int,
) -> dict:
    """Keep the injected span and align the clean paired window for long BIPIA contexts."""
    special_count = int(tokenizer.num_special_tokens_to_add(pair=False))
    content_limit = max_length - special_count
    token_ids = tokenizer.encode(text, add_special_tokens=False, truncation=False)
    attack_ids = tokenizer.encode(attack, add_special_tokens=False, truncation=False) if attack else []
    attack_start = -1
    attack_end = -1

    if is_poisoned and attack_ids and len(attack_ids) <= len(token_ids):
        for index in range(len(token_ids) - len(attack_ids) + 1):
            if token_ids[index:index + len(attack_ids)] == attack_ids:
                attack_start = index
                attack_end = index + len(attack_ids)
                break

    normalized_position = (position or "end").casefold()
    if len(token_ids) > content_limit:
        if is_poisoned and attack_start >= 0:
            desired = attack_start - max(0, (content_limit - (attack_end - attack_start)) // 2)
            start = min(max(0, desired), len(token_ids) - content_limit)
        elif normalized_position == "start":
            start = 0
        elif normalized_position == "middle":
            start = max(0, min(len(token_ids) - content_limit, len(token_ids) // 2 - content_limit // 2))
        else:
            # If the tokenized attack span could not be matched, keep the tail for an
            # end-position injection instead of silently truncating it away.
            start = max(0, len(token_ids) - content_limit)
        token_ids = token_ids[start:start + content_limit]

    encoded = tokenizer.prepare_for_model(
        token_ids,
        add_special_tokens=True,
        truncation=True,
        max_length=max_length,
        return_attention_mask=True,
    )
    return {
        key: value
        for key, value in encoded.items()
        if key in ("input_ids", "attention_mask", "token_type_ids")
    }


def determine_positive_index(model) -> int:
    label_map = {int(k): str(v) for k, v in (model.config.id2label or {}).items()}
    matches = [
        index for index, label in label_map.items()
        if ("inject" in label.casefold() or "malicious" in label.casefold() or "attack" in label.casefold())
        and "non" not in label.casefold()
    ]
    if matches:
        return matches[0]
    if int(model.config.num_labels) == 2:
        return 1
    raise RuntimeError(f"Could not determine positive class from checkpoint labels: {label_map}")


def main():
    parser = argparse.ArgumentParser(description="Warm-start the existing prompt-injection guard on diverse licensed training corpora.")
    parser.add_argument("--cache-dir", default=str(Path.home() / ".cache" / "graphrag-mixed-guard"))
    parser.add_argument("--output-dir", default="artifacts/mixed-corpus-guard")
    parser.add_argument("--model-dir", default="artifacts/mixed-corpus-guard/model")
    parser.add_argument("--base-model", default=BASE_MODEL)
    parser.add_argument("--max-bipia-rows", type=int, default=8000)
    parser.add_argument("--max-orbench-rows", type=int, default=8000)
    parser.add_argument("--notinject-train-fraction", type=float, default=0.50)
    parser.add_argument("--notinject-validation-fraction", type=float, default=0.25)
    parser.add_argument("--notinject-oversample-factor", type=int, default=4)
    parser.add_argument("--epochs", type=float, default=1.0)
    parser.add_argument("--train-batch-size", type=int, default=16)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=2)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=5e-6)
    parser.add_argument("--seed", type=int, default=20261014)
    args = parser.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    output_dir, model_dir = Path(args.output_dir), Path(args.model_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = str(Path(args.cache_dir))
    Path(cache_dir).mkdir(parents=True, exist_ok=True)

    start_utc = datetime.now(timezone.utc).isoformat()
    started = time.perf_counter()
    train_rows, validation_rows, data_info, notinject_manifest = load_mixed_rows(
        cache_dir,
        args.max_bipia_rows,
        args.max_orbench_rows,
        args.seed,
        args.notinject_train_fraction,
        args.notinject_validation_fraction,
        args.notinject_oversample_factor,
    )
    (output_dir / "notinject_partition_manifest.json").write_text(
        json.dumps(notinject_manifest, indent=2),
        encoding="utf-8",
    )

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)

    # ModernBERT checkpoints can enable reference torch.compile on their MLP
    # when Triton is present. Trainer / gradient backprop then encounters the
    # compiled callable while FX-tracing the training graph and fails with:
    # "using FX to symbolically trace a dynamo-optimized function". Fine-tuning
    # does not need this inference-only optimization, so disable it before model
    # construction rather than trying to unwrap a compiled layer after the fact.
    from transformers import AutoConfig
    model_config = AutoConfig.from_pretrained(args.base_model)
    if hasattr(model_config, "reference_compile"):
        model_config.reference_compile = False
    model = AutoModelForSequenceClassification.from_pretrained(
        args.base_model,
        config=model_config,
    )
    if hasattr(model.config, "reference_compile"):
        model.config.reference_compile = False
    if int(model.config.num_labels) != 2:
        raise RuntimeError(f"Expected binary classifier model, got {model.config.num_labels} labels")
    positive_index = determine_positive_index(model)
    negative_index = 1 - positive_index
    model.config.id2label = {
        negative_index: "BENIGN",
        positive_index: "INJECTION",
    }
    model.config.label2id = {
        "BENIGN": negative_index,
        "INJECTION": positive_index,
    }

    def tokenize_batch(batch):
        feature_rows = [
            prepare_training_window(
                text,
                tokenizer,
                attack,
                position,
                int(label) == 1,
                args.max_length,
            )
            for text, attack, position, label in zip(
                batch["text"], batch["attack"], batch["position"], batch["label"]
            )
        ]
        tokens = {
            key: [row[key] for row in feature_rows]
            for key in feature_rows[0]
        }
        tokens["labels"] = [
            positive_index if int(label) == 1 else negative_index
            for label in batch["label"]
        ]
        return tokens

    train_raw = Dataset.from_list(train_rows)
    validation_raw = Dataset.from_list(validation_rows)
    train_tokenized = train_raw.map(
        tokenize_batch,
        batched=True,
        remove_columns=train_raw.column_names,
        desc="Tokenizing combined injection corpus",
    )
    validation_tokenized = validation_raw.map(
        tokenize_batch,
        batched=True,
        remove_columns=validation_raw.column_names,
        desc="Tokenizing validation groups",
    )

    on_cuda = torch.cuda.is_available()
    if on_cuda:
        torch.backends.cuda.matmul.allow_tf32 = True
    training_args = TrainingArguments(
        output_dir=str(output_dir / "trainer"),
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.train_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        warmup_ratio=0.05,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=100,
        fp16=on_cuda,
        report_to=[],
        seed=args.seed,
        data_seed=args.seed,
        dataloader_num_workers=4,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=validation_tokenized,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        processing_class=tokenizer,
    )
    train_result = trainer.train()
    validation_result = trainer.evaluate()

    # Calibrate the operating threshold on the grouped validation partition only.
    # The external benchmark test rows are decontaminated from training, and the
    # threshold is frozen before the final held-out OOD reports are generated.
    val_predictions = trainer.predict(validation_tokenized)
    val_logits = torch.as_tensor(val_predictions.predictions, dtype=torch.float32)
    val_probabilities = torch.softmax(val_logits, dim=-1)[:, positive_index].cpu().tolist()
    val_rows = validation_rows
    if len(val_rows) != len(val_probabilities):
        raise RuntimeError(
            f"Validation alignment mismatch: {len(val_rows)} rows vs {len(val_probabilities)} scores"
        )

    def threshold_stats(rows, scores, threshold):
        if not rows:
            return {"n": 0, "tpr": None, "fpr": None, "tp": 0, "fp": 0, "tn": 0, "fn": 0}
        labels = [int(row["label"]) for row in rows]
        predictions = [int(float(score) >= threshold) for score in scores]
        tp = sum(y == 1 and pred == 1 for y, pred in zip(labels, predictions))
        fn = sum(y == 1 and pred == 0 for y, pred in zip(labels, predictions))
        fp = sum(y == 0 and pred == 1 for y, pred in zip(labels, predictions))
        tn = sum(y == 0 and pred == 0 for y, pred in zip(labels, predictions))
        positives = sum(y == 1 for y in labels)
        negatives = sum(y == 0 for y in labels)
        return {
            "n": len(rows), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "tpr": tp / positives if positives else None,
            "fpr": fp / negatives if negatives else None,
        }

    thresholds = [round(value, 2) for value in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95]]
    orbench_indices = [
        i for i, row in enumerate(val_rows)
        if str(row.get("source", "")).startswith("bench-llm/or-bench:or-bench-80k-train")
    ]
    notinject_validation_indices = [
        i for i, row in enumerate(val_rows)
        if str(row.get("source", "")).startswith("leolee99/NotInject:validation")
    ]
    benign_indices = [i for i, row in enumerate(val_rows) if int(row["label"]) == 0]
    bipia_positive_indices = [
        i for i, row in enumerate(val_rows)
        if int(row["label"]) == 1 and "bipia-injected-pair" in str(row.get("source", ""))
    ]
    threshold_records = []
    for threshold in thresholds:
        overall = threshold_stats(val_rows, val_probabilities, threshold)
        hard_rows = [val_rows[i] for i in orbench_indices]
        hard_scores = [val_probabilities[i] for i in orbench_indices]
        notinject_rows = [val_rows[i] for i in notinject_validation_indices]
        notinject_scores = [val_probabilities[i] for i in notinject_validation_indices]
        bipia_rows = [val_rows[i] for i in bipia_positive_indices]
        bipia_scores = [val_probabilities[i] for i in bipia_positive_indices]
        hard_stats = threshold_stats(hard_rows, hard_scores, threshold)
        notinject_stats = threshold_stats(notinject_rows, notinject_scores, threshold)
        bipia_stats = threshold_stats(bipia_rows, bipia_scores, threshold)
        threshold_records.append({
            "threshold": threshold,
            "overall_validation": overall,
            "all_benign_validation_fpr": threshold_stats(
                [val_rows[i] for i in benign_indices],
                [val_probabilities[i] for i in benign_indices],
                threshold,
            )["fpr"],
            "orbench_80k_validation": hard_stats,
            "notinject_validation": notinject_stats,
            "bipia_injected_validation": bipia_stats,
        })

    eligible_thresholds = [
        record for record in threshold_records
        if record["orbench_80k_validation"]["n"] >= 100
        and record["orbench_80k_validation"]["fpr"] is not None
        and record["orbench_80k_validation"]["fpr"] <= 0.05
        and record["all_benign_validation_fpr"] is not None
        and record["all_benign_validation_fpr"] <= 0.05
        and record["notinject_validation"]["n"] >= 50
        and record["notinject_validation"]["fpr"] is not None
        and record["notinject_validation"]["fpr"] <= 0.05
    ]
    if eligible_thresholds:
        selected_threshold = max(
            eligible_thresholds,
            key=lambda record: (
                record["bipia_injected_validation"]["tpr"] or 0.0,
                record["overall_validation"]["tpr"] or 0.0,
                record["threshold"],
            ),
        )
        calibration_feasible = True
        selection_reason = "Maximize BIPIA validation TPR subject to <=5% OR-Bench-80K, NotInject, and overall benign validation FPR."
    else:
        selected_threshold = min(
            threshold_records,
            key=lambda record: (
                max(
                    record["orbench_80k_validation"]["fpr"]
                    if record["orbench_80k_validation"]["fpr"] is not None else 1.0,
                    record["all_benign_validation_fpr"]
                    if record["all_benign_validation_fpr"] is not None else 1.0,
                ),
                -(record["bipia_injected_validation"]["tpr"] or 0.0),
                -record["threshold"],
            ),
        )
        calibration_feasible = False
        selection_reason = "No validation threshold satisfied OR-Bench, NotInject, and overall-benign 5% false-positive constraints; selected a diagnostic threshold. This model must not be promoted."

    calibration = {
        "calibration_split": "grouped training validation rows only; external test configs were not used to select the threshold",
        "threshold_grid": thresholds,
        "selected_threshold": selected_threshold["threshold"],
        "feasible": calibration_feasible,
        "selection_reason": selection_reason,
        "selected_record": selected_threshold,
        "all_thresholds": threshold_records,
        "orbench_validation_rows": len(orbench_indices),
        "bipia_injected_validation_rows": len(bipia_positive_indices),
    }

    trainer.save_model(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))
    (output_dir / "calibration.json").write_text(json.dumps(calibration, indent=2), encoding="utf-8")
    (output_dir / "calibrated_threshold.txt").write_text(f"{calibration['selected_threshold']:.2f}\n", encoding="utf-8")

    result = {
        "started_utc": start_utc,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "base_model": args.base_model,
        "base_model_license": "Apache-2.0",
        "training_dataset": data_info,
        "training_config": {
            "epochs": args.epochs,
            "learning_rate": args.learning_rate,
            "train_batch_size": args.train_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "max_length": args.max_length,
            "max_bipia_rows": args.max_bipia_rows,
            "max_orbench_rows": args.max_orbench_rows,
            "notinject_train_fraction": args.notinject_train_fraction,
            "notinject_validation_fraction": args.notinject_validation_fraction,
            "notinject_oversample_factor": args.notinject_oversample_factor,
            "positive_class_index": positive_index,
        },
        "train_metrics": train_result.metrics,
        "validation_metrics": validation_result,
        "threshold_calibration": calibration,
        "decision": "Candidate checkpoint only; it is not the production default unless held-out OOD tests beat the base guard and the calibrated threshold is feasible.",
        "model_dir": str(model_dir),
    }
    (output_dir / "training_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output_dir / "training_summary.md").write_text(
        "\n".join([
            "# Warm-start injection guard: mixed-corpus fine-tune",
            "",
            f"- Runtime: {result['elapsed_seconds']} seconds",
            f"- Base checkpoint: {args.base_model} (Apache-2.0)",
            "- Training sources: neuralchemy/Prompt-injection-dataset:full (Apache-2.0) + geodesic-research/bipia/bipia (CC-BY-SA-4.0) + bench-llm/or-bench:or-bench-80k train (CC-BY-4.0).",
            f"- Neuralchemy usable train examples: {data_info['mixed_dataset_usable']}",
            f"- BIPIA selected source rows: {data_info['bipia_selected_rows']}; paired documents: {data_info['bipia_pairs']}",
            f"- OR-Bench-80K benign hard negatives added: {data_info['orbench_rows_added']} (CC-BY-4.0 train split); exact overlap with held-out NotInject/OR-Bench-hard rows excluded: {data_info['orbench_rows_excluded_heldout_overlap']}",
            f"- Group split: train={data_info['train_examples']}, validation={data_info['validation_examples']}; exact cross-split duplicates removed={data_info['removed_exact_text_overlaps_from_validation']}",
            f"- Threshold calibration: {calibration['selected_threshold']:.2f}; feasible={calibration['feasible']}; OR-Bench FPR={calibration['selected_record']['orbench_80k_validation']['fpr']}; NotInject validation FPR={calibration['selected_record']['notinject_validation']['fpr']}; BIPIA TPR={calibration['selected_record']['bipia_injected_validation']['tpr']}",
            f"- Class counts train={data_info['train_class_counts']}; validation={data_info['validation_class_counts']}",
            f"- Epochs={args.epochs}, learning rate={args.learning_rate}, sequence length={args.max_length}; CUDA={on_cuda}",
            "",
            f"- Validation-calibrated threshold: {calibration['selected_threshold']:.2f}; constraints feasible={calibration['feasible']}.",
            f"- OR-Bench-80K exact overlaps with held-out NotInject/OR-Bench-hard samples excluded: {data_info['orbench_rows_excluded_heldout_overlap']}; duplicates against other training corpora excluded: {data_info['orbench_rows_excluded_duplicate']}.",
            "Candidate checkpoint only. Promote only if the calibrated threshold satisfies validation constraints and the same frozen-seed BIPIA/PIArena test sets improve while NotInject/OR-Bench-hard benign false positives remain <=5%.",
            "BIPIA-derived weights carry CC-BY-SA-4.0 attribution/share-alike obligations; review before redistribution.",
        ]) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

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
BASE_MODEL = "Horizon-Labs/prompt-injection-guard-base"


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


def load_mixed_rows(cache_dir: str, max_bipia_rows: int, seed: int):
    rng = random.Random(seed)
    grouped: dict[str, list[dict]] = defaultdict(list)
    raw_counts = {
        "mixed_dataset_rows": 0,
        "mixed_dataset_usable": 0,
        "bipia_dataset_rows": 0,
        "bipia_selected_rows": 0,
        "bipia_pairs": 0,
        "bipia_existing_attack_matches": 0,
        "bipia_reconstructed_attacks": 0,
    }

    # Keep augmented variants together: this dataset supplies group_id metadata.
    mixed = load_dataset(MIXED_DATASET, "full", split="train", cache_dir=cache_dir)
    raw_counts["mixed_dataset_rows"] = len(mixed)
    for row in mixed:
        text = str(row.get("text") or row.get("prompt") or "").strip()
        label = parse_label(row.get("label"))
        if len(text) < 8 or label is None:
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

    if len(grouped) < 20:
        raise RuntimeError(f"Insufficient distinct groups for leak-resistant split: {len(grouped)}")

    group_ids = list(grouped)
    rng.shuffle(group_ids)
    validation_groups = set(group_ids[:max(1, round(len(group_ids) * 0.10))])
    train_rows, validation_rows = [], []
    for group_id, examples in grouped.items():
        destination = validation_rows if group_id in validation_groups else train_rows
        destination.extend(examples)

    # Do not allow the exact same normalized document across the two partitions,
    # even if it appeared under two source datasets with different group IDs.
    train_text_hashes = {normalized_hash(row["text"]) for row in train_rows}
    before_val = len(validation_rows)
    validation_rows = [
        row for row in validation_rows
        if normalized_hash(row["text"]) not in train_text_hashes
    ]
    removed_cross_source_overlap = before_val - len(validation_rows)
    if not train_rows or not validation_rows:
        raise RuntimeError("Leak-resistant grouped split produced an empty partition")

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

    return train_rows, validation_rows, {
        **raw_counts,
        "distinct_groups": len(grouped),
        "train_examples": len(train_rows),
        "validation_examples": len(validation_rows),
        "train_class_counts": train_counts,
        "validation_class_counts": validation_counts,
        "context_grouped_split_seed": seed,
        "removed_exact_text_overlaps_from_validation": removed_cross_source_overlap,
        "license_notes": {
            "neuralchemy/Prompt-injection-dataset:full": "Apache-2.0 dataset card; group_id preserved for augmented variants",
            "geodesic-research/bipia/bipia": "CC-BY-SA-4.0; retain attribution and share-alike notice for redistributed derivative weights",
            "base_model": "Horizon-Labs/prompt-injection-guard-base (Apache-2.0 per model card)",
        },
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
    train_rows, validation_rows, data_info = load_mixed_rows(cache_dir, args.max_bipia_rows, args.seed)

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForSequenceClassification.from_pretrained(args.base_model)
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
        tokens = tokenizer(
            batch["text"],
            truncation=True,
            max_length=args.max_length,
            padding=False,
        )
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
    trainer.save_model(str(model_dir))
    tokenizer.save_pretrained(str(model_dir))

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
            "positive_class_index": positive_index,
        },
        "train_metrics": train_result.metrics,
        "validation_metrics": validation_result,
        "decision": "Candidate checkpoint only; it is not the production default unless held-out OOD tests beat the base guard.",
        "model_dir": str(model_dir),
    }
    (output_dir / "training_summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output_dir / "training_summary.md").write_text(
        "\n".join([
            "# Warm-start injection guard: mixed-corpus fine-tune",
            "",
            f"- Runtime: {result['elapsed_seconds']} seconds",
            f"- Base checkpoint: {args.base_model} (Apache-2.0)",
            "- Training sources: neuralchemy/Prompt-injection-dataset:full (Apache-2.0) + geodesic-research/bipia/bipia (CC-BY-SA-4.0)",
            f"- Neuralchemy usable train examples: {data_info['mixed_dataset_usable']}",
            f"- BIPIA selected source rows: {data_info['bipia_selected_rows']}; paired documents: {data_info['bipia_pairs']}",
            f"- Group split: train={data_info['train_examples']}, validation={data_info['validation_examples']}; exact cross-split duplicates removed={data_info['removed_exact_text_overlaps_from_validation']}",
            f"- Class counts train={data_info['train_class_counts']}; validation={data_info['validation_class_counts']}",
            f"- Epochs={args.epochs}, learning rate={args.learning_rate}, sequence length={args.max_length}; CUDA={on_cuda}",
            "",
            "Candidate checkpoint only. Promote only if the same frozen-seed BIPIA and PIArena test sets improve while NotInject/OR-Bench-hard benign false positives remain below the predeclared tolerance.",
            "BIPIA-derived weights carry CC-BY-SA-4.0 attribution/share-alike obligations; review before redistribution.",
        ]) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

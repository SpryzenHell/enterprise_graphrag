from __future__ import annotations

import json

from scripts.train_mixed_corpus_guard import (
    normalized_hash,
    split_labeled_validation_rows,
    split_notinject_rows,
    write_validation_jsonl,
)


def test_notinject_split_is_deterministic_disjoint_and_json_serializable():
    rows = [
        {"text": f"Benign customer-support request number {i} with routine context.", "label": 0}
        for i in range(120)
    ]
    train_a, validation_a, holdout_a, manifest_a = split_notinject_rows(
        rows, seed=20261016, train_fraction=0.50, validation_fraction=0.25
    )
    train_b, validation_b, holdout_b, manifest_b = split_notinject_rows(
        rows, seed=20261016, train_fraction=0.50, validation_fraction=0.25
    )

    hashes = lambda batch: {normalized_hash(row["text"]) for row in batch}
    train_hashes = hashes(train_a)
    validation_hashes = hashes(validation_a)
    holdout_hashes = hashes(holdout_a)

    assert train_hashes.isdisjoint(validation_hashes)
    assert train_hashes.isdisjoint(holdout_hashes)
    assert validation_hashes.isdisjoint(holdout_hashes)
    assert hashes(train_b) == train_hashes
    assert hashes(validation_b) == validation_hashes
    assert hashes(holdout_b) == holdout_hashes
    assert manifest_a["excluded_hashes"] == sorted(train_hashes | validation_hashes)
    assert manifest_a["excluded_hashes"] == manifest_b["excluded_hashes"]
    assert len(holdout_a) >= 25
    # The manifest must remain a plain JSON tree (no recursive self reference).
    json.loads(json.dumps(manifest_a))


def test_piarena_calibration_split_is_stratified_disjoint_and_deterministic():
    rows = []
    for label, kind in ((0, "benign"), (1, "injection")):
        for i in range(100):
            rows.append({
                "text": f"{kind} example {i}: distinct enterprise document payload for calibration.",
                "label": label,
            })

    validation_a, holdout_a, manifest_a = split_labeled_validation_rows(
        rows, seed=20261095, validation_fraction=0.20
    )
    validation_b, holdout_b, manifest_b = split_labeled_validation_rows(
        rows, seed=20261095, validation_fraction=0.20
    )

    hashes = lambda batch: {normalized_hash(row["text"]) for row in batch}
    validation_hashes = hashes(validation_a)
    holdout_hashes = hashes(holdout_a)
    assert validation_hashes.isdisjoint(holdout_hashes)
    assert hashes(validation_b) == validation_hashes
    assert hashes(holdout_b) == holdout_hashes
    assert sum(row["label"] == 0 for row in validation_a) == 20
    assert sum(row["label"] == 1 for row in validation_a) == 20
    assert sum(row["label"] == 0 for row in holdout_a) == 80
    assert sum(row["label"] == 1 for row in holdout_a) == 80
    assert manifest_a["excluded_hashes"] == sorted(validation_hashes)
    assert manifest_a["excluded_hashes"] == manifest_b["excluded_hashes"]


def test_validation_jsonl_handles_unicode_line_separator_characters(tmp_path):
    rows = [
        {
            "text": "A benign first line.\u2028This is the same JSON string, not a record delimiter.\u0085Still the same record.",
            "label": 0,
            "source": "notinject-validation",
        },
        {
            "text": "An injected context includes a paragraph mark here: \u2029 and an escaped newline here: \\n.",
            "label": 1,
            "source": "piarena-validation",
        },
    ]
    path = tmp_path / "validation.jsonl"

    count = write_validation_jsonl(path, rows)

    assert count == len(rows)
    # JSONL records are separated by literal LF only. Unicode separators inside
    # JSON strings must not be treated as physical records by str.splitlines().
    content = path.read_text(encoding="utf-8")
    records = content.split("\n")
    assert records[-1] == ""
    records = records[:-1]
    assert len(records) == 2
    parsed = [json.loads(line) for line in records]
    assert [row["text"] for row in parsed] == [row["text"] for row in rows]
    assert [row["label"] for row in parsed] == [0, 1]
    assert [row["source"] for row in parsed] == ["notinject-validation", "piarena-validation"]

from __future__ import annotations

import json

from scripts.train_mixed_corpus_guard import (
    normalized_hash,
    split_labeled_validation_rows,
    split_notinject_rows,
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

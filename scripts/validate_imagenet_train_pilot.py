"""Independently validate the local official ImageNet train pilot subset."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from statistics import median

from PIL import Image


EXPECTED_REPO = "ILSVRC/imagenet-1k"
EXPECTED_REVISION = "49e2ee26f3810fb5a7536bbf732a7b07389a47b5"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", type=Path)
    args = parser.parse_args()
    root = args.dataset_dir.resolve()
    metadata = json.loads((root / "metadata.json").read_text(encoding="utf-8"))
    source = metadata["source"]
    sample = metadata["sample"]

    assert source["dataset_repo"] == EXPECTED_REPO
    assert source["dataset_revision"] == EXPECTED_REVISION
    assert source["split_loaded"] == "train"
    assert source["streaming"] is True
    assert source["access_token_written_to_artifacts"] is False
    assert sample["selected_total"] == 5_000
    assert sample["finetune_train_count"] == 4_000
    assert sample["development_count"] == 1_000
    assert sample["development_name"] == "dev_train; drawn from official ILSVRC2012 train split"
    assert sample["pcf_validation_cohorts_loaded"] is False
    assert sample["official_imagenet_validation_split_loaded"] is False

    for line in (root / "checksums.sha256").read_text(encoding="ascii").splitlines():
        expected_hash, relative_name = line.split("  ", 1)
        assert sha256(root / relative_name) == expected_hash, relative_name

    with (root / "examples.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 5_000
    assert all(row["source_split"] == "train" for row in rows)
    assert all(row["source_repo"] == EXPECTED_REPO for row in rows)
    assert all(row["source_revision"] == EXPECTED_REVISION for row in rows)
    assert all(0 <= int(row["label_index"]) < 1_000 for row in rows)

    byte_hashes = [row["image_sha256"] for row in rows]
    pixel_hashes = [row["decoded_rgb_sha256"] for row in rows]
    assert len(set(byte_hashes)) == 5_000
    assert len(set(pixel_hashes)) == 5_000

    split_hashes: dict[str, set[str]] = {"finetune_train": set(), "dev_train": set()}
    split_counts: Counter[str] = Counter()
    label_counts: Counter[tuple[str, int]] = Counter()
    total_file_bytes = 0
    for row in rows:
        split = row["split"]
        assert split in split_hashes
        split_hashes[split].add(row["image_sha256"])
        split_counts[split] += 1
        label = int(row["label_index"])
        label_counts[(split, label)] += 1

        image_path = (root / row["image_relpath"]).resolve()
        assert image_path.is_relative_to(root)
        raw = image_path.read_bytes()
        total_file_bytes += len(raw)
        assert len(raw) == int(row["image_bytes"])
        assert hashlib.sha256(raw).hexdigest() == row["image_sha256"]
        with Image.open(io.BytesIO(raw)) as image:
            width, height = image.size
            image.load()
            rgb = image.convert("RGB")
            pixel_hash = hashlib.sha256(
                width.to_bytes(4, "big")
                + height.to_bytes(4, "big")
                + rgb.tobytes()
            ).hexdigest()
        assert (width, height) == (int(row["width"]), int(row["height"]))
        assert pixel_hash == row["decoded_rgb_sha256"]

    assert split_counts == {"finetune_train": 4_000, "dev_train": 1_000}
    assert not (split_hashes["finetune_train"] & split_hashes["dev_train"])
    assert total_file_bytes == sample["image_filesystem_bytes"]
    assert total_file_bytes == sample["saved_image_payload_bytes"]

    with (root / "label_counts.csv").open(newline="", encoding="utf-8") as handle:
        counts_rows = list(csv.DictReader(handle))
    assert len(counts_rows) == 2_000
    for row in counts_rows:
        key = (row["split"], int(row["label_index"]))
        assert int(row["count"]) == label_counts[key]
    nonzero_per_split = {
        split: sum(label_counts[(split, index)] > 0 for index in range(1_000))
        for split in split_hashes
    }
    total_per_class = [
        label_counts[("finetune_train", index)] + label_counts[("dev_train", index)]
        for index in range(1_000)
    ]

    summary = {
        "validation": "passed",
        "dataset_dir": str(root),
        "source": f"{EXPECTED_REPO}@{EXPECTED_REVISION} split=train",
        "examples": len(rows),
        "finetune_train": split_counts["finetune_train"],
        "dev_train": split_counts["dev_train"],
        "unique_encoded_sha256": len(set(byte_hashes)),
        "unique_decoded_rgb_sha256": len(set(pixel_hashes)),
        "all_images_decoded": True,
        "all_labels_valid": True,
        "split_disjoint": True,
        "distinct_labels_total": sum(value > 0 for value in total_per_class),
        "distinct_labels_by_split": nonzero_per_split,
        "examples_per_class_total_min_median_max": [
            min(total_per_class),
            median(total_per_class),
            max(total_per_class),
        ],
        "balanced_sample": False,
        "local_image_bytes": total_file_bytes,
        "stream_encoded_image_payload_bytes_read": source["encoded_image_payload_bytes_read"],
        "stream_rows_read_into_shuffle": source["rows_read_into_shuffle"],
        "classifier_label_map": metadata["classifier_label_mapping"],
        "checksums": metadata["files"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

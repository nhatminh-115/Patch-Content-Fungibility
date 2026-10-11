"""Freeze the mechanism, mu-tuning, and locked gate identities from dev_train."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path


SEED = 20261013


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset_dir", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with (args.dataset_dir / "examples.csv").open(newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["split"] == "dev_train"]
    if len(rows) != 1_000:
        raise RuntimeError(f"Expected 1,000 dev_train rows; found {len(rows)}")
    if len({row["image_sha256"] for row in rows}) != 1_000:
        raise RuntimeError("dev_train contains duplicate encoded image hashes")

    rows.sort(key=lambda row: row["image_sha256"])
    random.Random(SEED).shuffle(rows)
    groups = {
        "mechanism_dev": rows[:100],
        "mu_tune": rows[100:200],
        "dev_gate": rows[200:],
    }
    result = {
        "source_split": "official ILSVRC2012 train; development partition only",
        "dataset_revision": "49e2ee26f3810fb5a7536bbf732a7b07389a47b5",
        "source_manifest_sha256": hashlib.sha256(
            (args.dataset_dir / "examples.csv").read_bytes()
        ).hexdigest(),
        "partition_seed": SEED,
        "identity": "encoded image SHA-256",
        "partitions": {
            name: [
                {
                    "image_sha256": row["image_sha256"],
                    "label_index": int(row["label_index"]),
                    "image_relpath": row["image_relpath"],
                }
                for row in selected
            ]
            for name, selected in groups.items()
        },
    }
    flat = [item["image_sha256"] for selected in groups.values() for item in selected]
    if len(flat) != 1_000 or len(set(flat)) != 1_000:
        raise RuntimeError("Frozen dev partitions are not exactly disjoint and exhaustive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": {k: len(v) for k, v in groups.items()},
                      "output": str(args.output.resolve()),
                      "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()

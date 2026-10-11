"""Acquire a small, reproducible subset from the official ILSVRC2012 train split.

This script never downloads the complete ImageNet archive. It uses the locally
authenticated Hugging Face session (token=True) and does not print, serialize, or
otherwise expose the access token. Raw image files stay in an ignored local_data/
directory; only the acquisition script and metadata manifest belong in Git.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import platform
import random
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import PIL
from PIL import Image as PILImage


REPO_ID = "ILSVRC/imagenet-1k"
DEFAULT_REVISION = "49e2ee26f3810fb5a7536bbf732a7b07389a47b5"
DEFAULT_SAMPLE_SEED = 20261011
DEFAULT_SPLIT_SEED = 20261012
DEFAULT_SHUFFLE_BUFFER = 2_000
TOTAL_EXAMPLES = 5_000
TRAIN_EXAMPLES = 4_000
DEV_EXAMPLES = 1_000
MODEL_NAME = "deit_small_patch16_224.fb_in1k"
PREFLIGHT_IMAGES = 10
PREFLIGHT_ENCODED_BYTES = 1_108_823


def _normalized_aliases(name: str) -> set[str]:
    return {
        " ".join(re.sub(r"[^a-z0-9]+", " ", alias.lower()).split())
        for alias in name.split(",")
    }


def verify_classifier_label_map(label_names: list[str]) -> dict[str, Any]:
    """Check official ImageNet-1k label indexing against timm's canonical map."""
    from timm import create_model
    from timm.data.imagenet_info import ImageNetInfo

    model = create_model(MODEL_NAME, pretrained=False)
    timm_info = ImageNetInfo("imagenet-1k")
    synsets = timm_info.label_names()
    descriptions = timm_info.label_descriptions(detailed=False)

    if len(label_names) != 1_000 or len(synsets) != 1_000:
        raise RuntimeError(
            f"Expected 1,000 classes; source={len(label_names)}, timm={len(synsets)}"
        )
    if len(set(synsets)) != 1_000 or synsets != sorted(synsets):
        raise RuntimeError("timm's ImageNet-1k synset index is not 1,000 unique sorted WNIDs")
    if model.num_classes != 1_000 or model.pretrained_cfg.get("num_classes") != 1_000:
        raise RuntimeError("The selected timm DeiT-S checkpoint configuration is not 1,000-way")

    alias_mismatches = []
    for index, (source_name, timm_name) in enumerate(zip(label_names, descriptions)):
        if not (_normalized_aliases(source_name) & _normalized_aliases(timm_name)):
            alias_mismatches.append(
                {"index": index, "source_name": source_name, "timm_name": timm_name}
            )

    # This official snapshot calls class 517 "crane2" where timm's canonical
    # WordNet lemma is "crane". Both lists use the sorted ILSVRC synset index;
    # all other class descriptions share an alias. Do not remap integer labels.
    expected_alias_mismatch = [
        {"index": 517, "source_name": "crane2", "timm_name": "crane"}
    ]
    if alias_mismatches != expected_alias_mismatch:
        raise RuntimeError(
            "Unexpected source/timm class-name mapping differences: "
            + json.dumps(alias_mismatches[:10], ensure_ascii=False)
        )

    return {
        "source_class_count": len(label_names),
        "timm_synset_count": len(synsets),
        "timm_synsets_unique_and_sorted": True,
        "classifier_model": MODEL_NAME,
        "classifier_num_classes": model.num_classes,
        "label_offset": model.pretrained_cfg.get("label_offset", 0),
        "integer_label_remapping": "none; both use the sorted ILSVRC2012 synset index",
        "description_alias_mismatches": alias_mismatches,
    }


def _decode_and_hash(raw: bytes) -> tuple[str, str, int, int, str]:
    with PILImage.open(io.BytesIO(raw)) as image:
        image_format = (image.format or "UNKNOWN").upper()
        width, height = image.size
        image.verify()
    with PILImage.open(io.BytesIO(raw)) as image:
        image.load()
        rgb = image.convert("RGB")
        pixel_hash = hashlib.sha256(
            width.to_bytes(4, "big")
            + height.to_bytes(4, "big")
            + rgb.tobytes()
        ).hexdigest()
    byte_hash = hashlib.sha256(raw).hexdigest()
    return byte_hash, pixel_hash, width, height, image_format


def _extension(image_format: str) -> str:
    return {
        "JPEG": ".jpg",
        "JPG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
        "BMP": ".bmp",
        "TIFF": ".tif",
    }.get(image_format, ".img")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def acquire(output_dir: Path, revision: str, seed: int, split_seed: int, buffer_size: int) -> dict[str, Any]:
    from datasets import Image as HFImage
    from datasets import load_dataset
    from huggingface_hub import HfApi, get_token
    import datasets
    import huggingface_hub
    import timm
    import torch

    if not get_token():
        raise RuntimeError("No local Hugging Face token found; run `hf auth login` locally.")
    HfApi().whoami()  # Auth check only; never print the account profile or token.
    info = HfApi().dataset_info(REPO_ID, revision=revision, files_metadata=False)
    if info.sha != revision:
        raise RuntimeError(f"Pinned revision mismatch: requested={revision}, returned={info.sha}")

    final_dir = output_dir.resolve()
    partial_dir = final_dir.with_name(final_dir.name + ".partial")
    if final_dir.exists() or partial_dir.exists():
        raise FileExistsError(
            f"Refusing to overwrite existing data directory: {final_dir} or {partial_dir}"
        )
    partial_dir.mkdir(parents=True)
    image_dir = partial_dir / "images"
    image_dir.mkdir()

    source = load_dataset(
        REPO_ID,
        split="train",
        streaming=True,
        token=True,
        revision=revision,
    ).cast_column("image", HFImage(decode=False))
    label_feature = source.features.get("label")
    label_names = getattr(label_feature, "names", None)
    if not label_names:
        raise RuntimeError("Official train stream did not expose a 1,000-class label map")
    mapping_check = verify_classifier_label_map(list(label_names))

    source_stats = {"rows_read_into_shuffle": 0, "encoded_image_payload_bytes_read": 0}

    def count_source_payload(row: dict[str, Any]) -> dict[str, Any]:
        image_record = row.get("image")
        raw = image_record.get("bytes") if isinstance(image_record, dict) else None
        if not raw:
            raise RuntimeError("Train stream did not provide encoded image bytes")
        source_stats["rows_read_into_shuffle"] += 1
        source_stats["encoded_image_payload_bytes_read"] += len(raw)
        return row

    shuffled = source.map(count_source_payload).shuffle(seed=seed, buffer_size=buffer_size)
    selected: list[dict[str, Any]] = []
    seen_byte_hashes: set[str] = set()
    seen_pixel_hashes: set[str] = set()
    duplicate_payloads_skipped = 0

    for row in shuffled:
        label = int(row["label"])
        if not 0 <= label < 1_000:
            raise RuntimeError(f"Out-of-range ImageNet label encountered: {label}")
        image_record = row["image"]
        raw = image_record.get("bytes") if isinstance(image_record, dict) else None
        if not raw:
            raise RuntimeError("Train stream did not provide encoded image bytes")
        byte_hash, pixel_hash, width, height, image_format = _decode_and_hash(raw)
        if byte_hash in seen_byte_hashes or pixel_hash in seen_pixel_hashes:
            duplicate_payloads_skipped += 1
            continue

        relative_path = Path("images") / f"{byte_hash}{_extension(image_format)}"
        image_path = partial_dir / relative_path
        image_path.write_bytes(raw)
        seen_byte_hashes.add(byte_hash)
        seen_pixel_hashes.add(pixel_hash)
        selected.append(
            {
                "sample_order": len(selected),
                "source_split": "train",
                "label_index": label,
                "label_name": label_names[label],
                "image_sha256": byte_hash,
                "decoded_rgb_sha256": pixel_hash,
                "image_relpath": relative_path.as_posix(),
                "image_bytes": len(raw),
                "width": width,
                "height": height,
                "format": image_format,
            }
        )
        if len(selected) == TOTAL_EXAMPLES:
            break

    if len(selected) != TOTAL_EXAMPLES:
        raise RuntimeError(
            f"Train stream ended after {len(selected)} unique images; expected {TOTAL_EXAMPLES}"
        )
    if len({row["image_sha256"] for row in selected}) != TOTAL_EXAMPLES:
        raise RuntimeError("Encoded-image hashes are not unique")
    if len({row["decoded_rgb_sha256"] for row in selected}) != TOTAL_EXAMPLES:
        raise RuntimeError("Decoded-pixel hashes are not unique")

    permutation = list(range(TOTAL_EXAMPLES))
    random.Random(split_seed).shuffle(permutation)
    dev_indices = set(permutation[:DEV_EXAMPLES])
    manifest_rows = []
    for index, row in enumerate(selected):
        manifest_rows.append(
            {
                **row,
                "split": "dev_train" if index in dev_indices else "finetune_train",
                "source_repo": REPO_ID,
                "source_revision": revision,
            }
        )
    train_rows = [row for row in manifest_rows if row["split"] == "finetune_train"]
    dev_rows = [row for row in manifest_rows if row["split"] == "dev_train"]
    if len(train_rows) != TRAIN_EXAMPLES or len(dev_rows) != DEV_EXAMPLES:
        raise RuntimeError(f"Incorrect split sizes: train={len(train_rows)}, dev={len(dev_rows)}")
    if {r["image_sha256"] for r in train_rows} & {r["image_sha256"] for r in dev_rows}:
        raise RuntimeError("Train and development samples overlap")

    manifest_fields = [
        "sample_order",
        "split",
        "source_repo",
        "source_revision",
        "source_split",
        "label_index",
        "label_name",
        "image_sha256",
        "decoded_rgb_sha256",
        "image_relpath",
        "image_bytes",
        "width",
        "height",
        "format",
    ]
    manifest_path = partial_dir / "examples.csv"
    _write_csv(manifest_path, manifest_rows, manifest_fields)

    counts = Counter((row["split"], row["label_index"]) for row in manifest_rows)
    count_rows = []
    for split_name in ("finetune_train", "dev_train"):
        for label_index, label_name in enumerate(label_names):
            count_rows.append(
                {
                    "split": split_name,
                    "label_index": label_index,
                    "label_name": label_name,
                    "count": counts[(split_name, label_index)],
                }
            )
    _write_csv(
        partial_dir / "label_counts.csv",
        count_rows,
        ["split", "label_index", "label_name", "count"],
    )

    saved_image_bytes = sum(row["image_bytes"] for row in manifest_rows)
    disk_bytes_before_metadata = sum(path.stat().st_size for path in image_dir.iterdir())
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    count_sha256 = hashlib.sha256((partial_dir / "label_counts.csv").read_bytes()).hexdigest()
    metadata = {
        "source": {
            "dataset_repo": REPO_ID,
            "dataset_revision": revision,
            "split_loaded": "train",
            "official_source_check": "Hugging Face repository card identifies ILSVRC2012/ImageNet-1k",
            "streaming": True,
            "shuffle_seed": seed,
            "shuffle_buffer_size": buffer_size,
            "sampling_method": "datasets IterableDataset.shuffle(seed, buffer_size); first 5,000 unique encoded and decoded-image hashes",
            "rows_read_into_shuffle": source_stats["rows_read_into_shuffle"],
            "encoded_image_payload_bytes_read": source_stats["encoded_image_payload_bytes_read"],
            "duplicate_payloads_skipped": duplicate_payloads_skipped,
            "access_token_written_to_artifacts": False,
        },
        "sample": {
            "selected_total": TOTAL_EXAMPLES,
            "finetune_train_count": len(train_rows),
            "development_count": len(dev_rows),
            "development_name": "dev_train; drawn from official ILSVRC2012 train split",
            "split_seed": split_seed,
            "balanced_sampling": False,
            "unique_encoded_hashes": len(seen_byte_hashes),
            "unique_decoded_rgb_hashes": len(seen_pixel_hashes),
            "all_images_decoded": True,
            "all_labels_in_0_999": True,
            "train_dev_disjoint": True,
            "pcf_validation_cohorts_loaded": False,
            "official_imagenet_validation_split_loaded": False,
            "preflight_train_images_decoded": PREFLIGHT_IMAGES,
            "preflight_encoded_image_payload_bytes": PREFLIGHT_ENCODED_BYTES,
            "saved_image_payload_bytes": saved_image_bytes,
            "image_filesystem_bytes": disk_bytes_before_metadata,
        },
        "transforms": {
            "stored_images": "original encoded bytes; no resize, crop, or re-encoding during acquisition",
            "fine_tuning": [
                "Resize(256, bicubic)",
                "RandomCrop(224)",
                "RandomHorizontalFlip(0.5)",
                "ToTensor()",
                "Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])",
            ],
            "development": [
                "Resize(256, bicubic)",
                "CenterCrop(224)",
                "ToTensor()",
                "Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])",
            ],
        },
        "classifier_label_mapping": mapping_check,
        "files": {
            "manifest": "examples.csv",
            "manifest_sha256": manifest_sha256,
            "label_counts": "label_counts.csv",
            "label_counts_sha256": count_sha256,
            "images_directory": "images/",
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "datasets": datasets.__version__,
            "huggingface_hub": huggingface_hub.__version__,
            "timm": timm.__version__,
            "torch": torch.__version__,
            "pillow": PIL.__version__,
        },
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    metadata_path = partial_dir / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    metadata_sha256 = hashlib.sha256(metadata_path.read_bytes()).hexdigest()
    (partial_dir / "checksums.sha256").write_text(
        f"{manifest_sha256}  examples.csv\n"
        f"{count_sha256}  label_counts.csv\n"
        f"{metadata_sha256}  metadata.json\n",
        encoding="ascii",
    )

    final_dir.parent.mkdir(parents=True, exist_ok=True)
    os.replace(partial_dir, final_dir)
    return {
        "output_dir": str(final_dir),
        "dataset_revision": revision,
        "selected": len(manifest_rows),
        "finetune_train": len(train_rows),
        "dev_train": len(dev_rows),
        "rows_read_into_shuffle": source_stats["rows_read_into_shuffle"],
        "encoded_image_payload_bytes_read": source_stats["encoded_image_payload_bytes_read"],
        "saved_image_payload_bytes": saved_image_bytes,
        "filesystem_image_bytes": disk_bytes_before_metadata,
        "duplicate_payloads_skipped": duplicate_payloads_skipped,
        "distinct_labels_total": len({row["label_index"] for row in manifest_rows}),
        "manifest_sha256": manifest_sha256,
        "label_map_alias_mismatches": mapping_check["description_alias_mismatches"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "local_data"
        / "imagenet_train_5k_seed20261011",
    )
    parser.add_argument("--revision", default=DEFAULT_REVISION)
    parser.add_argument("--seed", type=int, default=DEFAULT_SAMPLE_SEED)
    parser.add_argument("--split-seed", type=int, default=DEFAULT_SPLIT_SEED)
    parser.add_argument("--buffer-size", type=int, default=DEFAULT_SHUFFLE_BUFFER)
    args = parser.parse_args()
    if args.buffer_size < 1:
        parser.error("--buffer-size must be positive")
    summary = acquire(
        args.output_dir,
        revision=args.revision,
        seed=args.seed,
        split_seed=args.split_seed,
        buffer_size=args.buffer_size,
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

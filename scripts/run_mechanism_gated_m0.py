"""Run M0 parity, clean/compressed accuracy, and frozen-weight mechanism screen."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms import InterpolationMode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.mechanism_gated_coarsening import (  # noqa: E402
    centered_logit_distortion,
    forward_clean_manual,
    forward_compressed,
    mechanism_diagnostics,
)


MODEL_NAME = "deit_small_patch16_224.fb_in1k"
DATA_DIR = ROOT / "local_data" / "imagenet_train_5k_seed20261011"
DEV_PARTITIONS = ROOT / "artifacts" / "imagenet_train_5k_seed20261011" / "dev_partitions.json"


class PilotImages(Dataset):
    def __init__(self, data_root: Path, rows: list[dict], training: bool = False):
        self.data_root = data_root
        self.rows = rows
        if training:
            self.transform = transforms.Compose([
                transforms.Resize(256, interpolation=InterpolationMode.BICUBIC),
                transforms.RandomCrop(224),
                transforms.RandomHorizontalFlip(0.5),
                transforms.ToTensor(),
                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize(256, interpolation=InterpolationMode.BICUBIC),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
            ])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(self.data_root / row["image_relpath"]) as image:
            image = image.convert("RGB")
            return self.transform(image), int(row["label_index"]), row["image_sha256"]


def read_manifest(data_root: Path) -> list[dict]:
    with (data_root / "examples.csv").open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bootstrap_mean_ci(values: list[float], seed: int, reps: int = 10_000) -> list[float]:
    array = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    samples = rng.integers(0, len(array), size=(reps, len(array)))
    means = array[samples].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def state_dict_sha256(model) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        digest.update(name.encode("utf-8"))
        value = tensor.detach().cpu().contiguous()
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(np.asarray(value.shape, dtype=np.int64).tobytes())
        digest.update(value.numpy().tobytes())
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    data_root = args.data_dir.resolve()
    output_path = args.output or data_root / "runs" / "m0.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    import timm
    from scipy.stats import spearmanr

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the frozen pilot's bounded M0 run")
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
    torch.manual_seed(20261020)
    torch.cuda.manual_seed_all(20261020)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.cuda.reset_peak_memory_stats(device)

    model = timm.create_model(MODEL_NAME, pretrained=True).to(device).eval()
    if len(model.blocks) != 12 or model.embed_dim != 384 or model.blocks[0].attn.num_heads != 6:
        raise RuntimeError("Loaded checkpoint architecture does not match frozen DeiT-Small semantics")
    checkpoint_hash = state_dict_sha256(model)

    manifest = read_manifest(data_root)
    dev_rows = [row for row in manifest if row["split"] == "dev_train"]
    with DEV_PARTITIONS.open(encoding="utf-8") as handle:
        partition_doc = json.load(handle)
    mechanism_hashes = [r["image_sha256"] for r in partition_doc["partitions"]["mechanism_dev"]]
    row_by_hash = {row["image_sha256"]: row for row in dev_rows}
    mechanism_rows = [row_by_hash[h] for h in mechanism_hashes[:64]]
    if len(dev_rows) != 1_000 or len(mechanism_rows) != 64:
        raise RuntimeError("M0 requires all 1,000 dev_train rows and 64 frozen mechanism_dev rows")

    clean_loader = DataLoader(PilotImages(data_root, dev_rows), batch_size=args.batch_size,
                              shuffle=False, num_workers=0, pin_memory=True)
    correct_clean = correct_pool = 0
    seen = 0
    distortions: list[float] = []
    clean_manual_max = 0.0
    start_time = time.perf_counter()
    with torch.inference_mode():
        for batch_idx, (images, labels, _) in enumerate(clean_loader):
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            clean = model(images)
            pooled = forward_compressed(model, images)
            if batch_idx == 0:
                clean_manual = forward_clean_manual(model, images)
                clean_manual_max = float((clean - clean_manual).abs().max().cpu())
            correct_clean += int((clean.argmax(-1) == labels).sum().cpu())
            correct_pool += int((pooled.argmax(-1) == labels).sum().cpu())
            distortions.extend(centered_logit_distortion(pooled, clean).cpu().tolist())
            seen += labels.numel()
    accuracy_seconds = time.perf_counter() - start_time
    if seen != 1_000:
        raise RuntimeError(f"Expected 1,000 dev_train images, evaluated {seen}")

    mechanism_loader = DataLoader(PilotImages(data_root, mechanism_rows), batch_size=8,
                                  shuffle=False, num_workers=0, pin_memory=True)
    diagnostics: dict[str, list[float]] = {}
    cell_correlations: list[float] = []
    max_identity_residual = 0.0
    with torch.inference_mode():
        for images, _, _ in mechanism_loader:
            images = images.to(device, non_blocking=True)
            hidden = model.patch_embed(images)
            hidden = model._pos_embed(hidden)
            hidden = model.patch_drop(hidden)
            hidden = model.norm_pre(hidden)
            for block_idx in range(7):
                hidden = model.blocks[block_idx](hidden)
            batch_metrics = mechanism_diagnostics(model, hidden)
            max_identity_residual = max(
                max_identity_residual,
                float(batch_metrics.covariance_residual_max.max().cpu()),
            )
            for name in (
                "omega", "attention_logit_std", "covariance_norm", "actual_attention_error",
                "block_output_error", "final_logit_distortion", "group_mass_tv",
                "pooled_key_mismatch", "pooled_value_mismatch", "full_entropy",
                "compressed_entropy", "covariance_ratio",
            ):
                diagnostics.setdefault(name, []).extend(getattr(batch_metrics, name).cpu().tolist())
            for image_idx in range(batch_metrics.cell_omega.shape[0]):
                omega_cells = batch_metrics.cell_omega[image_idx].flatten().cpu().numpy()
                cov_cells = batch_metrics.cell_covariance_norm[image_idx].flatten().cpu().numpy()
                corr = float(spearmanr(omega_cells, cov_cells).statistic)
                cell_correlations.append(corr)

    corr_ci = bootstrap_mean_ci(cell_correlations, seed=20261031)
    ratio_ci = bootstrap_mean_ci(diagnostics["covariance_ratio"], seed=20261031)
    median_ratio = float(np.median(diagnostics["covariance_ratio"]))
    median_corr = float(np.median(cell_correlations))
    identity_pass = max_identity_residual <= 1e-5
    mechanism_pass = (
        median_ratio >= 0.10 and ratio_ci[0] > 0.05
        and median_corr >= 0.25 and corr_ci[0] > 0.10
    )
    report = {
        "gate": "M0",
        "passed": bool(identity_pass and mechanism_pass and clean_manual_max <= 1e-5),
        "identity_pass": bool(identity_pass),
        "pretraining_mechanism_screen_pass": bool(mechanism_pass),
        "model": MODEL_NAME,
        "model_state_dict_sha256": checkpoint_hash,
        "pretrained_cfg": model.pretrained_cfg,
        "device": torch.cuda.get_device_name(device),
        "cuda_runtime": torch.version.cuda,
        "torch": torch.__version__,
        "timm": timm.__version__,
        "batch_size": args.batch_size,
        "dev_split": "dev_train; official ILSVRC2012 train only",
        "dev_images": seen,
        "clean_top1": correct_clean / seen,
        "untrained_pool_top1": correct_pool / seen,
        "untrained_pool_accuracy_delta_pp": 100 * (correct_pool - correct_clean) / seen,
        "mean_centered_logit_distortion": float(np.mean(distortions)),
        "clean_manual_max_abs_logit_error": clean_manual_max,
        "dev_accuracy_seconds": accuracy_seconds,
        "mechanism_images": len(cell_correlations),
        "covariance_identity_max_abs_residual": max_identity_residual,
        "median_covariance_ratio": median_ratio,
        "mean_covariance_ratio_bootstrap_95ci": ratio_ci,
        "median_image_spearman_omega_vs_projected_covariance": median_corr,
        "mean_image_spearman_bootstrap_95ci": corr_ci,
        "mechanism_metrics": {
            name: {
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std": float(np.std(values, ddof=1)),
            }
            for name, values in diagnostics.items()
        },
        "gpu_peak_allocated_bytes": int(torch.cuda.max_memory_allocated(device)),
        "gpu_peak_reserved_bytes": int(torch.cuda.max_memory_reserved(device)),
        "partition_manifest_sha256": partition_doc["source_manifest_sha256"],
        "mechanism_dev_hashes": mechanism_hashes[:64],
    }
    output_path.write_text(json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "gate", "passed", "identity_pass", "pretraining_mechanism_screen_pass",
        "clean_top1", "untrained_pool_top1", "mean_centered_logit_distortion",
        "covariance_identity_max_abs_residual", "median_covariance_ratio",
        "mean_covariance_ratio_bootstrap_95ci",
        "median_image_spearman_omega_vs_projected_covariance",
        "mean_image_spearman_bootstrap_95ci", "gpu_peak_allocated_bytes",
    )}, indent=2))
    print(f"report={output_path.resolve()}")


if __name__ == "__main__":
    main()

"""Run the preregistered 512-image paired M1 target-engagement screen."""

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
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.transforms import InterpolationMode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.mechanism_gated_coarsening import (  # noqa: E402
    centered_logit_distortion,
    forward_compressed_from_block6,
    forward_compressed_with_omega,
    mechanism_diagnostics,
)
from scripts.run_mechanism_gated_m0 import (  # noqa: E402
    MODEL_NAME,
    bootstrap_mean_ci,
    state_dict_sha256,
)


DATA_DIR = ROOT / "local_data" / "imagenet_train_5k_seed20261011"
PARTITION_PATH = ROOT / "artifacts" / "imagenet_train_5k_seed20261011" / "dev_partitions.json"
TRAIN_SEED = 20261021
M1_MU = 0.01
TEMPERATURE = 2.0


class PilotImages(Dataset):
    def __init__(self, data_root: Path, rows: list[dict], training: bool):
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


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def train_arm(arm: str, mu: float, data_root: Path, out_dir: Path,
              initial_sha256: str, teacher, device: torch.device,
              amp_dtype: torch.dtype | None) -> dict:
    import timm

    set_seed(TRAIN_SEED)
    student = timm.create_model(MODEL_NAME, pretrained=True).to(device)
    student.train()
    student_sha = state_dict_sha256(student)
    if student_sha != initial_sha256:
        raise RuntimeError("Student arm did not start from the identical pretrained checkpoint")
    optimizer = torch.optim.AdamW(student.parameters(), lr=1e-5, weight_decay=0.05)
    with (data_root / "examples.csv").open(newline="", encoding="utf-8") as handle:
        examples = list(csv.DictReader(handle))
    rows = [row for row in examples if row["split"] == "finetune_train"][:512]
    if len(rows) != 512:
        raise RuntimeError(f"M1 expected 512 finetune_train examples; got {len(rows)}")
    loader = DataLoader(PilotImages(data_root, rows, training=True), batch_size=8,
                        shuffle=False, num_workers=0, pin_memory=True)
    torch.cuda.reset_peak_memory_stats(device)
    sums = {"loss": 0.0, "ce": 0.0, "kl": 0.0, "omega": 0.0}
    start = time.perf_counter()
    for step, (images, labels, _) in enumerate(loader, start=1):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        use_amp = amp_dtype is not None
        with torch.no_grad():
            with torch.autocast("cuda", dtype=amp_dtype or torch.float32, enabled=use_amp):
                teacher_logits = teacher(images)
        with torch.autocast("cuda", dtype=amp_dtype or torch.float32, enabled=use_amp):
            student_logits, omega = forward_compressed_with_omega(student, images)
            ce = F.cross_entropy(student_logits.float(), labels)
            kl = F.kl_div(
                F.log_softmax(student_logits.float() / TEMPERATURE, dim=-1),
                F.softmax(teacher_logits.float() / TEMPERATURE, dim=-1),
                reduction="batchmean",
            ) * TEMPERATURE**2
            loss = ce + kl + mu * omega.float().mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(student.parameters(), max_norm=1.0)
        optimizer.step()
        sums["loss"] += float(loss.detach())
        sums["ce"] += float(ce.detach())
        sums["kl"] += float(kl.detach())
        sums["omega"] += float(omega.detach().mean())
        if step % 16 == 0 or step == len(loader):
            print(f"{arm}: step {step}/{len(loader)} loss={sums['loss']/step:.4f}", flush=True)

    elapsed = time.perf_counter() - start
    checkpoint = out_dir / f"m1_{arm.lower()}_seed{TRAIN_SEED}.pt"
    torch.save({
        "model": student.state_dict(),
        "arm": arm,
        "mu": mu,
        "seed": TRAIN_SEED,
        "initial_state_dict_sha256": student_sha,
        "steps": len(loader),
    }, checkpoint)
    report = {
        "arm": arm,
        "mu": mu,
        "seed": TRAIN_SEED,
        "images": len(rows),
        "steps": len(loader),
        "mean_loss": sums["loss"] / len(loader),
        "mean_ce": sums["ce"] / len(loader),
        "mean_kl": sums["kl"] / len(loader),
        "mean_omega": sums["omega"] / len(loader),
        "training_seconds": elapsed,
        "peak_allocated_bytes": int(torch.cuda.max_memory_allocated(device)),
        "checkpoint": str(checkpoint.resolve()),
    }
    del optimizer, student
    torch.cuda.empty_cache()
    return report


@torch.inference_mode()
def evaluate_arm(arm: str, data_root: Path, rows: list[dict], checkpoint: Path,
                 teacher, device: torch.device, batch_size: int) -> dict:
    import timm

    payload = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model = timm.create_model(MODEL_NAME, pretrained=False).to(device).eval()
    model.load_state_dict(payload["model"], strict=True)
    loader = DataLoader(PilotImages(data_root, rows, training=False), batch_size=batch_size,
                        shuffle=False, num_workers=0, pin_memory=True)
    metrics: dict[str, list[float]] = {}
    per_image = []
    for images, labels, hashes in loader:
        images = images.to(device, non_blocking=True)
        labels_device = labels.to(device, non_blocking=True)
        hidden = model.patch_embed(images)
        hidden = model._pos_embed(hidden)
        hidden = model.patch_drop(hidden)
        hidden = model.norm_pre(hidden)
        for idx in range(7):
            hidden = model.blocks[idx](hidden)
        diag = mechanism_diagnostics(model, hidden)
        compressed_logits = forward_compressed_from_block6(model, hidden)
        clean_logits = model(images)
        teacher_logits = teacher(images)
        teacher_distortion = centered_logit_distortion(compressed_logits, teacher_logits)
        compressed_correct = compressed_logits.argmax(-1).eq(labels_device)
        clean_correct = clean_logits.argmax(-1).eq(labels_device)
        teacher_correct = teacher_logits.argmax(-1).eq(labels_device)
        batch_fields = {
            "omega": diag.omega,
            "attention_logit_std": diag.attention_logit_std,
            "covariance_norm": diag.covariance_norm,
            "actual_attention_error": diag.actual_attention_error,
            "block_output_error": diag.block_output_error,
            "final_logit_distortion": diag.final_logit_distortion,
            "teacher_centered_logit_distortion": teacher_distortion,
            "group_mass_tv": diag.group_mass_tv,
            "pooled_key_mismatch": diag.pooled_key_mismatch,
            "pooled_value_mismatch": diag.pooled_value_mismatch,
            "full_entropy": diag.full_entropy,
            "compressed_entropy": diag.compressed_entropy,
            "covariance_ratio": diag.covariance_ratio,
            "compressed_correct": compressed_correct.float(),
            "clean_correct": clean_correct.float(),
            "teacher_correct": teacher_correct.float(),
            "covariance_residual_max": diag.covariance_residual_max,
        }
        for key, values in batch_fields.items():
            metrics.setdefault(key, []).extend(values.cpu().tolist())
        for idx, identity in enumerate(hashes):
            per_image.append({
                "image_sha256": identity,
                "label_index": int(labels[idx]),
                "omega": float(diag.omega[idx].cpu()),
                "attention_logit_std": float(diag.attention_logit_std[idx].cpu()),
                "covariance_norm": float(diag.covariance_norm[idx].cpu()),
                "actual_attention_error": float(diag.actual_attention_error[idx].cpu()),
                "block_output_error": float(diag.block_output_error[idx].cpu()),
                "final_logit_distortion": float(diag.final_logit_distortion[idx].cpu()),
                "teacher_centered_logit_distortion": float(teacher_distortion[idx].cpu()),
                "group_mass_tv": float(diag.group_mass_tv[idx].cpu()),
                "pooled_key_mismatch": float(diag.pooled_key_mismatch[idx].cpu()),
                "pooled_value_mismatch": float(diag.pooled_value_mismatch[idx].cpu()),
                "full_entropy": float(diag.full_entropy[idx].cpu()),
                "compressed_entropy": float(diag.compressed_entropy[idx].cpu()),
                "covariance_ratio": float(diag.covariance_ratio[idx].cpu()),
                "compressed_correct": bool(compressed_correct[idx].cpu()),
                "clean_correct": bool(clean_correct[idx].cpu()),
                "teacher_correct": bool(teacher_correct[idx].cpu()),
                "covariance_residual_max": float(diag.covariance_residual_max[idx].cpu()),
            })

    summary = {k: {
        "mean": float(np.mean(v)), "median": float(np.median(v)),
        "std": float(np.std(v, ddof=1)),
    } for k, v in metrics.items()}
    summary["top1"] = float(np.mean(metrics["compressed_correct"]))
    summary["clean_top1"] = float(np.mean(metrics["clean_correct"]))
    summary["teacher_top1"] = float(np.mean(metrics["teacher_correct"]))
    summary["per_image"] = per_image
    del model
    torch.cuda.empty_cache()
    return summary


def paired_bootstrap_ci(diffs: np.ndarray, seed: int, reps: int = 10_000) -> list[float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, diffs.shape[0], size=(reps, diffs.shape[0]))
    means = diffs[indices].mean(axis=1)
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    data_root = args.data_dir.resolve()
    out_dir = data_root / "runs" / "m1"
    out_dir.mkdir(parents=True, exist_ok=True)

    import timm
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for the preregistered M1 training screen")
    device = torch.device("cuda:0")
    torch.cuda.set_device(device)
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    amp_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else None
    print(f"device={torch.cuda.get_device_name(device)} amp={amp_dtype}", flush=True)

    teacher = timm.create_model(MODEL_NAME, pretrained=True).to(device).eval()
    initial_sha = state_dict_sha256(teacher)
    for parameter in teacher.parameters():
        parameter.requires_grad_(False)
    arm_reports = []
    for arm, mu in (("C", 0.0), ("D", M1_MU)):
        arm_reports.append(train_arm(arm, mu, data_root, out_dir, initial_sha,
                                     teacher, device, amp_dtype))

    with (data_root / "examples.csv").open(newline="", encoding="utf-8") as handle:
        examples = list(csv.DictReader(handle))
    with PARTITION_PATH.open(encoding="utf-8") as handle:
        partition_doc = json.load(handle)
    dev_by_hash = {r["image_sha256"]: r for r in examples if r["split"] == "dev_train"}
    mechanism_hashes = [item["image_sha256"] for item in partition_doc["partitions"]["mechanism_dev"]]
    mechanism_rows = [dev_by_hash[identity] for identity in mechanism_hashes]
    c_path = Path(arm_reports[0]["checkpoint"])
    d_path = Path(arm_reports[1]["checkpoint"])
    print("Evaluating C on frozen mechanism_dev", flush=True)
    eval_c = evaluate_arm("C", data_root, mechanism_rows, c_path, teacher, device, args.batch_size)
    print("Evaluating D on frozen mechanism_dev", flush=True)
    eval_d = evaluate_arm("D", data_root, mechanism_rows, d_path, teacher, device, args.batch_size)

    c_by_hash = {row["image_sha256"]: row for row in eval_c["per_image"]}
    d_by_hash = {row["image_sha256"]: row for row in eval_d["per_image"]}
    ordered_hashes = mechanism_hashes
    comparisons = {}
    for metric in ("covariance_norm", "actual_attention_error"):
        c_values = np.asarray([c_by_hash[h][metric] for h in ordered_hashes], dtype=np.float64)
        d_values = np.asarray([d_by_hash[h][metric] for h in ordered_hashes], dtype=np.float64)
        diffs = d_values - c_values
        comparisons[metric] = {
            "c_mean": float(c_values.mean()),
            "d_mean": float(d_values.mean()),
            "c_median": float(np.median(c_values)),
            "d_median": float(np.median(d_values)),
            "median_relative_reduction": float(1.0 - np.median(d_values) / np.median(c_values)),
            "paired_mean_difference_d_minus_c": float(diffs.mean()),
            "paired_bootstrap_95ci": paired_bootstrap_ci(diffs, seed=20261031),
        }
    cov_ok = (
        comparisons["covariance_norm"]["median_relative_reduction"] >= 0.10
        and comparisons["covariance_norm"]["paired_bootstrap_95ci"][1] < 0
    )
    attn_ok = (
        comparisons["actual_attention_error"]["median_relative_reduction"] >= 0.05
        and comparisons["actual_attention_error"]["paired_bootstrap_95ci"][1] < 0
    )
    max_identity = max(
        eval_c["covariance_residual_max"]["mean"],
        eval_d["covariance_residual_max"]["mean"],
    )
    result = {
        "gate": "M1",
        "passed": bool(cov_ok and attn_ok and max_identity <= 1e-5),
        "seed": TRAIN_SEED,
        "fixed_mu": M1_MU,
        "teacher_checkpoint_sha256": initial_sha,
        "optimizer": "AdamW(lr=1e-5, weight_decay=0.05)",
        "batch_size": 8,
        "amp": str(amp_dtype) if amp_dtype is not None else "FP32",
        "schedule": "one epoch over first 512 finetune_train examples in manifest order",
        "training": arm_reports,
        "mechanism_dev_hashes": mechanism_hashes,
        "paired_comparisons": comparisons,
        "covariance_gate_pass": bool(cov_ok),
        "actual_attention_gate_pass": bool(attn_ok),
        "covariance_identity_max_abs_residual": max_identity,
        "C": {k: v for k, v in eval_c.items() if k != "per_image"},
        "D": {k: v for k, v in eval_d.items() if k != "per_image"},
        "per_image": {
            h: {"C": c_by_hash[h], "D": d_by_hash[h]} for h in ordered_hashes
        },
        "bootstrap_seed": 20261031,
    }
    output_path = out_dir / "m1.json"
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": "M1",
        "passed": result["passed"],
        "covariance_comparison": comparisons["covariance_norm"],
        "actual_attention_comparison": comparisons["actual_attention_error"],
        "C_top1": eval_c["top1"],
        "D_top1": eval_d["top1"],
        "C_omega": eval_c["omega"],
        "D_omega": eval_d["omega"],
        "C_full_entropy": eval_c["full_entropy"],
        "D_full_entropy": eval_d["full_entropy"],
        "max_identity_residual": max_identity,
        "output": str(output_path.resolve()),
    }, indent=2))


if __name__ == "__main__":
    main()

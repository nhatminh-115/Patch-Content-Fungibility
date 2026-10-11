"""Post-G2 diagnostic: trace distortion while cosine and student states diverge."""

import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from PIL import Image
import torch

from patch_fungibility.counterfactual_merge import (
    apply_actions, candidate_pool, forward_suffix_batch, initial_state,
    normalized_distortion, state_batch,
)
from patch_fungibility.dense_fraction_models import load_model_and_transform
from scripts.run_counterfactual_merge_pilot import SEED_CANDIDATE, calibration_records, image_bytes, prefix
from scripts.train_counterfactual_merge_scorer import PairScorer, score_candidates


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-dir", default="outputs/counterfactual_merge_student")
    args = parser.parse_args()
    root = Path(args.student_dir)
    gate = json.loads((root / "gate_g2.json").read_text())
    if gate["G2_pass"]:
        raise RuntimeError("This diagnostic is intended for a failed G2")
    manifest = json.loads((root / "manifest.json").read_text())
    previous = pd.read_csv(root / "rollout_per_image.csv")
    records, _ = calibration_records()
    val = image_bytes([r for r in records if r["cohort"] == "stability"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    rows = []
    for model_key, depth in (("deit_small", 8), ("vit_base", 7)):
        model, transform, meta = load_model_and_transform(model_key, device)
        mean = np.array(manifest["models"][model_key]["feature_mean"], dtype=np.float32)
        std = np.array(manifest["models"][model_key]["feature_std"], dtype=np.float32)
        scorer = PairScorer(meta["embed_dim"])
        scorer.load_state_dict(torch.load(root / f"{model_key}_counterfactual_pair.pt",
                                          map_location="cpu", weights_only=True))
        scorer.to(device).eval()
        with torch.inference_mode():
            for n, r in enumerate(val):
                x = transform(Image.open(io.BytesIO(r["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
                full = initial_state(prefix(model, model_key, depth, x))
                clean = model(x)
                for method in ("cosine", "counterfactual_pair"):
                    state = full
                    round_no = 0
                    while True:
                        hidden, mass = state_batch([state])
                        logits = forward_suffix_batch(model, model_key, depth, hidden, mass)
                        rows.append({
                            "model": model_key, "global_index": r["global_index"],
                            "method": method, "round": round_no,
                            "patch_count": state.count,
                            "distortion": float(normalized_distortion(logits, clean)[0]),
                            "max_multiplicity": float(state.multiplicities.max()),
                        })
                        if state.count == 49:
                            earlier = previous[(previous.model == model_key) &
                                               (previous.global_index == r["global_index"]) &
                                               (previous.method == method) & (previous.budget == 49)]
                            if len(earlier) != 1 or abs(rows[-1]["distortion"] - float(earlier.distortion.iloc[0])) > 1e-6:
                                raise RuntimeError("Diagnostic final state differs from recorded rollout")
                            break
                        seed = SEED_CANDIDATE + r["global_index"] + 1009 * state.count + 7919 * (196 - state.count)
                        candidates = candidate_pool(state, seed)
                        scores = score_candidates(method, {"counterfactual_pair": scorer},
                                                  state, candidates, mean, std, device)
                        chosen = []
                        used = set()
                        for ix in np.argsort(scores, kind="stable"):
                            c = candidates[int(ix)]
                            if c["source"] not in used:
                                chosen.append((c["source"], c["destination"]))
                                used.add(c["source"])
                            if len(chosen) == min(16, state.count - 49):
                                break
                        state = apply_actions(state, chosen)
                        round_no += 1
                if (n + 1) % 16 == 0:
                    print(f"{model_key}: {n + 1}/{len(val)}", flush=True)
        del model, scorer
    frame = pd.DataFrame(rows)
    frame.to_csv(root / "rollout_diagnostic_per_image.csv", index=False)
    summary = frame.groupby(["model", "round", "patch_count", "method"]).agg(
        n_images=("distortion", "size"), mean_distortion=("distortion", "mean"),
        mean_max_multiplicity=("max_multiplicity", "mean"),
    ).reset_index()
    summary.to_csv(root / "rollout_diagnostic_summary.csv", index=False)
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()

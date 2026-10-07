"""Join validated actual-model accuracy and timing into a Pareto table."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "fungibility_real_final"


def main():
    acc = pd.read_csv(OUT / "real_accuracy_summary.csv")
    timing = pd.read_csv(OUT / "real_throughput_summary.csv")
    if set(acc.n.unique()) != {1000}:
        raise ValueError("Frontier requires N=1,000 actual accuracy rows")
    method_map = {
        "Clean": "Clean",
        "Hybrid Group Mean": "Hybrid Group Mean",
        "Static Feature-PCA q=16": "Static Feature-PCA q=16",
        "Static Feature-PCA q=32": "Static Feature-PCA q=32",
        "Selective Feature-PCA q16 target30": "Selective Feature-PCA q16 target30",
    }
    rows = []
    for arch, g in timing.groupby("architecture"):
        b50 = int(g.budget_tokens.iloc[0])
        a = acc[(acc.architecture == arch) & (acc.budget_tokens == b50)].set_index("method")
        for _, t in g.iterrows():
            if t.method not in method_map:
                continue
            method = method_map[t.method]
            if method not in a.index:
                raise ValueError(f"Missing accuracy for {arch}, {method}, budget {b50}")
            ar = a.loc[method]
            rows.append({"architecture": arch, "method": method,
                         "budget_tokens": b50, "n": int(ar.n),
                         "correct_count": int(ar.correct_count),
                         "top1_accuracy": float(ar.top1_accuracy),
                         "batch_size": int(t.batch_size),
                         "batch_latency_ms": float(t.batch_latency_ms),
                         "per_image_ms": float(t.per_image_ms),
                         "img_per_sec": float(t.img_per_sec),
                         "speedup_vs_clean": None,
                         "pareto_optimal": True,
                         "dominated_by": ""})
    df = pd.DataFrame(rows)
    for (arch, bs), idx in df.groupby(["architecture", "batch_size"]).groups.items():
        part = df.loc[idx]
        clean_speed = float(part.loc[part.method == "Clean", "img_per_sec"].iloc[0])
        df.loc[idx, "speedup_vs_clean"] = df.loc[idx, "img_per_sec"] / clean_speed
        for row_index, row in part.iterrows():
            dominators = part[(part.top1_accuracy >= row.top1_accuracy)
                              & (part.img_per_sec >= row.img_per_sec)
                              & ((part.top1_accuracy > row.top1_accuracy)
                                 | (part.img_per_sec > row.img_per_sec))]
            df.loc[row_index, "pareto_optimal"] = dominators.empty
            df.loc[row_index, "dominated_by"] = "; ".join(dominators.method.tolist())
    df.to_csv(OUT / "real_accuracy_throughput_frontier.csv", index=False)
    print(df[df.pareto_optimal].groupby(["architecture", "batch_size"]).method.apply(list).to_string())


if __name__ == "__main__":
    main()

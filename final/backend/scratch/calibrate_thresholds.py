"""
PART A CALIBRATION SCRIPT
Runs all 520 scenarios through the current engine, collects per-scenario
PageRank max-Z-scores, and finds cutoffs that match the known distribution:
  SAFE=396, WATCH=74, WARNING=35, COMPOUND_CRITICAL=15
"""

import os, sys, json
import numpy as np

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.engine.data_loader import ScenarioDataLoader
from app.engine.graph_engine import GraphEngine

# Load scenarios
base_data_dir = os.path.join(os.path.dirname(backend_dir), "data")
data_file = os.path.join(base_data_dir, "scenarios_500.json")
with open(data_file, "r", encoding="utf-8") as f:
    scenarios = json.load(f)

loader = ScenarioDataLoader(data_dir=base_data_dir)
loader.load_all()

engine = GraphEngine(restart_probability=0.15)

records = []  # (gt_label, max_pr_score, max_pr_zscore)

for sc in scenarios:
    nodes = loader.scenario_to_nodes(sc)
    distances = loader.get_all_sensor_permit_distances(sc)

    engine.set_nodes(nodes)
    engine.set_sensor_permit_distances(distances)

    current_anomalies = {n.id: n.z_score for n in nodes
                         if n.category.value == "SENSOR" and n.z_score is not None}
    anomalous_seeds = [nid for nid, z in current_anomalies.items() if abs(z) > 2.0]

    if anomalous_seeds:
        engine.build_adjacency_matrix(current_anomalies)
        pr_scores = engine.personalized_pagerank(anomalous_seeds)
        values = list(pr_scores.values())
    else:
        values = [1.0 / len(nodes)] * len(nodes) if nodes else [0.0]

    all_vals = np.array(values)
    mean_pr = float(np.mean(all_vals))
    std_pr = float(np.std(all_vals))

    max_pr = float(np.max(all_vals))
    if std_pr > 1e-9:
        max_z = (max_pr - mean_pr) / std_pr
    else:
        max_z = 0.0

    records.append({
        "gt": sc.get("ground_truth_label", "SAFE"),
        "max_pr": max_pr,
        "max_z": max_z,
    })

gt_labels = [r["gt"] for r in records]
max_zs = np.array([r["max_z"] for r in records])

print(f"\nDataset: {len(records)} scenarios")
print(f"GT dist: {dict(zip(*np.unique(gt_labels, return_counts=True)))}")
print(f"\nMax-Z stats: mean={max_zs.mean():.3f} std={max_zs.std():.3f} "
      f"min={max_zs.min():.3f} max={max_zs.max():.3f}")

# Print percentiles to pick cutoffs
for pct in [70, 80, 87, 93, 97]:
    print(f"  P{pct}: {np.percentile(max_zs, pct):.3f}")

# Grid-search cutoffs to match desired distribution
target = {"SAFE": 396, "WATCH": 74, "WARNING": 35, "COMPOUND_CRITICAL": 15}
# Note: COMPOUND_CRITICAL comes from RuleGuard (always fires on top of PageRank)
# so PageRank only needs to cover SAFE vs WATCH vs WARNING

best = None
best_err = 1e9

# Try cutoffs for WATCH (z_watch) and WARNING (z_warn), CRITICAL is RuleGuard-only
for z_warn in np.arange(0.5, 4.0, 0.05):
    for z_watch in np.arange(0.1, z_warn, 0.05):
        predicted = []
        for r in records:
            if r["max_z"] >= z_warn:
                predicted.append("WARNING")
            elif r["max_z"] >= z_watch:
                predicted.append("WATCH")
            else:
                predicted.append("SAFE")
        counts = {k: predicted.count(k) for k in ["SAFE","WATCH","WARNING"]}
        err = (abs(counts["SAFE"] - target["SAFE"]) +
               abs(counts["WATCH"] - target["WATCH"]) +
               abs(counts["WARNING"] - target["WARNING"]))
        if err < best_err:
            best_err = err
            best = (z_watch, z_warn, counts)

z_watch, z_warn, counts = best
print(f"\nBest cutoffs: WATCH z>={z_watch:.2f}, WARNING z>={z_warn:.2f}  (err={best_err})")
print(f"  Predicted SAFE={counts['SAFE']}, WATCH={counts['WATCH']}, WARNING={counts['WARNING']}")
print(f"  Target    SAFE={target['SAFE']}, WATCH={target['WATCH']}, WARNING={target['WARNING']}")

# Show per-GT-label max_z distributions
for label in ["SAFE", "WATCH", "WARNING", "COMPOUND_CRITICAL"]:
    vals = [r["max_z"] for r in records if r["gt"] == label]
    if vals:
        print(f"\n  GT={label} (n={len(vals)}): "
              f"mean_z={np.mean(vals):.2f} std={np.std(vals):.2f} "
              f"min={np.min(vals):.2f} max={np.max(vals):.2f}")

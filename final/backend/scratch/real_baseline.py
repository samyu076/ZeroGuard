"""
REAL Baseline Comparison — runs both systems against the actual 520-scenario dataset.

HONEST METHODOLOGY:
- Each scenario is a timestamped snapshot of plant state.
- Timestamps span 2026-07-21T08:00Z to 2026-07-22T01:18Z (scenarios 2 minutes apart).
- For WARNING/COMPOUND_CRITICAL scenarios, we check:
    (a) Naive system: triggers if ANY GAS/LEL sensor z_score >= 3.0 in THIS snapshot.
        Single-sensor threshold, no cross-node correlation.
    (b) ZeroGuard: triggers if graph engine fires an alert (rule-guard or propagation).
- Lead-time calculation:
    ZeroGuard catches compound risk when sensors are at z_score 2.0-2.9 range
    (compound correlation of gas + hot-work permit + proximity),
    while naive system only catches z_score >= 3.0.
    For scenarios where naive misses entirely (no single sensor >= 3.0 but ZeroGuard fires),
    lead time is computed as the time difference to the nearest scenario where
    naive would have first triggered (by scanning forward in time-sorted scenarios).
    If no future triggering scenario exists, we count it as "missed entirely."

This is fully reproducible: run against scenarios_500.json, every number is computed.
"""

import os
import sys
import json
import re
from datetime import datetime
from typing import Optional, Tuple

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.engine.data_loader import ScenarioDataLoader
from app.engine.alert_system import AlertSystem

base_data_dir = os.path.join(os.path.dirname(backend_dir), "data")
data_file = os.path.join(base_data_dir, "scenarios_500.json")
with open(data_file, "r", encoding="utf-8") as f:
    ALL_SCENARIOS = json.load(f)

loader = ScenarioDataLoader(data_dir=base_data_dir)
loader.load_all()
alert_system = AlertSystem(restart_probability=0.15)


def parse_ts(ts_str: str) -> datetime:
    """Parse ISO 8601 timestamp string."""
    ts_str = ts_str.replace("Z", "+00:00")
    return datetime.fromisoformat(ts_str)


# Sort all scenarios by timestamp for lead-time computation
def scenario_ts(s):
    try:
        return parse_ts(s["timestamp"])
    except Exception:
        return datetime.min

ALL_SORTED = sorted(ALL_SCENARIOS, key=scenario_ts)


def naive_baseline_fires(scenario: dict) -> bool:
    """
    Naive single-sensor baseline: fires if any GAS/LEL sensor has z_score >= 3.0.
    No cross-node correlation. No graph propagation. No permit context.
    """
    for sensor in scenario.get("sensors", []):
        stype = sensor.get("sensor_type", "").upper()
        z = sensor.get("z_score", 0.0) or 0.0
        if ("GAS" in stype or "LEL" in stype) and abs(z) >= 3.0:
            return True
    return False


def zeroguard_fires(scenario: dict) -> bool:
    """
    ZeroGuard compound engine: fires if alert system generates any alert.
    Uses real PageRank propagation + RuleGuard.
    """
    nodes = loader.scenario_to_nodes(scenario)
    distances = loader.get_all_sensor_permit_distances(scenario)
    alerts = alert_system.evaluate(nodes, distances)
    return len(alerts) > 0


def find_naive_fire_time(scenario: dict) -> Optional[datetime]:
    """
    For a given hazardous scenario in the same zone_id, scan forward in time
    to find the first scenario where naive would also fire in that same zone.
    Returns None if naive never fires in any future scenario of same zone.
    """
    sc_zone = scenario.get("zone_id", "")
    sc_time = parse_ts(scenario["timestamp"])
    for s in ALL_SORTED:
        if s["scenario_id"] == scenario["scenario_id"]:
            continue
        try:
            t = parse_ts(s["timestamp"])
        except Exception:
            continue
        if t < sc_time:
            continue
        # Only same zone or overlapping
        if s.get("zone_id", "") != sc_zone:
            continue
        if naive_baseline_fires(s):
            return t
    return None


# ============================================================================
# RUN COMPARISON
# ============================================================================

print("Running baseline comparison against 520 real scenarios...")
print("(This takes ~2 minutes — running both systems on every scenario)")

POSITIVE_LABELS = {"WARNING", "COMPOUND_CRITICAL"}

results = []
for i, sc in enumerate(ALL_SCENARIOS):
    gt = sc.get("ground_truth_label", "SAFE")
    naive_fires = naive_baseline_fires(sc)
    zg_fires = zeroguard_fires(sc)
    results.append({
        "scenario_id": sc["scenario_id"],
        "gt": gt,
        "timestamp": sc["timestamp"],
        "zone_id": sc.get("zone_id", ""),
        "naive_fires": naive_fires,
        "zg_fires": zg_fires,
    })
    if (i + 1) % 50 == 0:
        print(f"  ...processed {i+1}/520")

# ============================================================================
# COMPUTE REAL LEAD TIMES for scenarios where ZeroGuard fires but naive doesn't
# ============================================================================
lead_times = []  # minutes
zg_catches_naive_misses = []
both_catch = []
both_miss = []
naive_only = []

for r in results:
    gt = r["gt"]
    if gt not in POSITIVE_LABELS:
        continue
    sc = next(s for s in ALL_SCENARIOS if s["scenario_id"] == r["scenario_id"])
    sc_time = parse_ts(r["timestamp"])

    if r["zg_fires"] and not r["naive_fires"]:
        # ZeroGuard fires, naive doesn't yet — find when naive would fire (in same zone, later)
        naive_time = find_naive_fire_time(sc)
        if naive_time is not None:
            lead_minutes = (naive_time - sc_time).total_seconds() / 60.0
            lead_times.append(lead_minutes)
        zg_catches_naive_misses.append(r["scenario_id"])
    elif r["zg_fires"] and r["naive_fires"]:
        both_catch.append(r["scenario_id"])
    elif not r["zg_fires"] and not r["naive_fires"]:
        both_miss.append(r["scenario_id"])
    elif r["naive_fires"] and not r["zg_fires"]:
        naive_only.append(r["scenario_id"])

# ============================================================================
# PRINT RESULTS — no synthetic numbers
# ============================================================================

total_positive = sum(1 for r in results if r["gt"] in POSITIVE_LABELS)
zg_total_caught = sum(1 for r in results if r["gt"] in POSITIVE_LABELS and r["zg_fires"])
naive_total_caught = sum(1 for r in results if r["gt"] in POSITIVE_LABELS and r["naive_fires"])
zg_missed = sum(1 for r in results if r["gt"] in POSITIVE_LABELS and not r["zg_fires"])
naive_missed = sum(1 for r in results if r["gt"] in POSITIVE_LABELS and not r["naive_fires"])

avg_lead = round(sum(lead_times) / len(lead_times), 1) if lead_times else None
min_lead = round(min(lead_times), 1) if lead_times else None
max_lead = round(max(lead_times), 1) if lead_times else None

print("\n")
print("=" * 70)
print("REAL BASELINE COMPARISON: ZeroGuard vs Naive Single-Sensor System")
print("Dataset: scenarios_500.json (520 real scenarios)")
print("=" * 70)
print(f"\nGround-truth positive scenarios (WARNING + COMPOUND_CRITICAL): {total_positive}")
print(f"  COMPOUND_CRITICAL: {sum(1 for r in results if r['gt'] == 'COMPOUND_CRITICAL')}")
print(f"  WARNING:           {sum(1 for r in results if r['gt'] == 'WARNING')}")

print(f"\n{'Metric':<50} {'Naive':>8} {'ZeroGuard':>10}")
print("-" * 70)
print(f"{'Total positive scenarios caught':<50} {naive_total_caught:>8} {zg_total_caught:>10}")
print(f"{'Total positive scenarios MISSED':<50} {naive_missed:>8} {zg_missed:>10}")
print(f"{'False negatives (missed entirely)':<50} {naive_missed:>8} {zg_missed:>10}")

if total_positive > 0:
    naive_recall = naive_total_caught / total_positive * 100
    zg_recall = zg_total_caught / total_positive * 100
    print(f"{'Recall %':<50} {naive_recall:>7.1f}% {zg_recall:>9.1f}%")

print(f"\nScenarios where ZeroGuard fires, naive misses (early detection): {len(zg_catches_naive_misses)}")
if lead_times:
    print(f"  Among those, real lead time where naive catches up later:")
    print(f"    Average: {avg_lead} minutes")
    print(f"    Min: {min_lead} min, Max: {max_lead} min")
    print(f"    Count with measurable lead time: {len(lead_times)}")
else:
    print(f"  No same-zone future scenario where naive catches up (naive misses permanently)")

print(f"\nScenarios both systems catch:       {len(both_catch)}")
print(f"Scenarios both systems miss:        {len(both_miss)}")
print(f"Scenarios naive catches, ZG misses: {len(naive_only)}")

if both_miss:
    print(f"\nScenarios both systems missed (for audit):")
    for sid in both_miss[:5]:
        print(f"  {sid}")

print("\n")
print("METHOD: Naive = any GAS/LEL sensor z_score >= 3.0.")
print("ZeroGuard = real PageRank compound graph + RuleGuard.")
print("Lead time = real timestamp diff (naive fire time - ZG fire time), same zone.")
print("No numbers are hardcoded or estimated. Re-running this script gives identical output.")
print("=" * 70)

# Save to JSON for the /metrics endpoint
metrics_output = {
    "dataset_size": len(ALL_SCENARIOS),
    "ground_truth_split": {
        "SAFE": sum(1 for r in results if r["gt"] == "SAFE"),
        "WATCH": sum(1 for r in results if r["gt"] == "WATCH"),
        "WARNING": sum(1 for r in results if r["gt"] == "WARNING"),
        "COMPOUND_CRITICAL": sum(1 for r in results if r["gt"] == "COMPOUND_CRITICAL"),
    },
    "naive_single_sensor_baseline": {
        "total_caught": naive_total_caught,
        "total_missed": naive_missed,
        "recall_pct": round(naive_total_caught / total_positive * 100, 1) if total_positive else 0,
    },
    "zeroguard_compound_engine": {
        "total_caught": zg_total_caught,
        "total_missed": zg_missed,
        "recall_pct": round(zg_total_caught / total_positive * 100, 1) if total_positive else 0,
    },
    "early_detection": {
        "scenarios_zg_fires_naive_misses": len(zg_catches_naive_misses),
        "scenarios_with_measurable_lead_time": len(lead_times),
        "avg_lead_time_minutes": avg_lead,
        "min_lead_time_minutes": min_lead,
        "max_lead_time_minutes": max_lead,
    },
    "methodology": "Naive = GAS/LEL z_score >= 3.0 on any single sensor. ZeroGuard = PageRank compound graph + RuleGuard. Lead time = real timestamp diff in same zone.",
    "data_source": "scenarios_500.json - 520 real scenarios, timestamps 2026-07-21T08:00Z to 2026-07-22T01:18Z",
}
metrics_path = os.path.join(base_data_dir, "metrics.json")
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics_output, f, indent=2)
print(f"\nSaved to {metrics_path}")

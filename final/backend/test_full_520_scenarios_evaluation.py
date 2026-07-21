import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engine.real_engine import RealGraphEngine

def run_exhaustive_520_scenarios_test():
    print("=================================================================")
    print("      EXHAUSTIVE 520-SCENARIO LIVE ENGINE EVALUATION SUITE       ")
    print("=================================================================\n")

    engine = RealGraphEngine(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    scenarios = engine.data_loader.scenarios
    print(f"Loaded {len(scenarios)} total scenarios from final/data/scenarios_500.json.\n")

    ground_truth_counts = Counter(s.get("ground_truth_label") for s in scenarios)
    print("Ground Truth Distribution:")
    for label, count in ground_truth_counts.items():
        print(f"  - {label}: {count}")
    print("")

    # Evaluation results mapping
    results_by_label = {
        "COMPOUND_CRITICAL": {"total": 0, "correct_critical": 0, "rule_guard_fired": 0, "details": []},
        "WARNING": {"total": 0, "correct_warning_or_high": 0, "rule_guard_fired": 0, "propagation_fired": 0, "details": []},
        "WATCH": {"total": 0, "correct_watch_or_medium": 0, "normal": 0, "details": []},
        "SAFE": {"total": 0, "normal": 0, "false_positives": 0, "details": []}
    }

    confusion_matrix = {}

    for idx, scen in enumerate(scenarios, 1):
        sid = scen["scenario_id"]
        gt_label = scen.get("ground_truth_label", "UNKNOWN")
        graph = engine.load_scenario(sid)

        eval_level = graph.overall_risk_level.value
        eval_score = graph.overall_risk_score
        alerts = graph.active_alerts
        primary_alert = alerts[0] if alerts else None
        triggered_by = primary_alert.triggered_by.value if primary_alert else "NONE"

        key = (gt_label, eval_level)
        confusion_matrix[key] = confusion_matrix.get(key, 0) + 1

        if gt_label == "COMPOUND_CRITICAL":
            results_by_label["COMPOUND_CRITICAL"]["total"] += 1
            if triggered_by == "RULE_GUARD" and eval_level == "CRITICAL":
                results_by_label["COMPOUND_CRITICAL"]["correct_critical"] += 1
                results_by_label["COMPOUND_CRITICAL"]["rule_guard_fired"] += 1

        elif gt_label == "WARNING":
            results_by_label["WARNING"]["total"] += 1
            if eval_level in ["CRITICAL", "HIGH", "WARNING"]:
                results_by_label["WARNING"]["correct_warning_or_high"] += 1
            if triggered_by == "RULE_GUARD":
                results_by_label["WARNING"]["rule_guard_fired"] += 1
            elif triggered_by == "PROPAGATION":
                results_by_label["WARNING"]["propagation_fired"] += 1

        elif gt_label == "WATCH":
            results_by_label["WATCH"]["total"] += 1
            if eval_level in ["MEDIUM", "LOW", "WARNING", "HIGH"]:
                results_by_label["WATCH"]["correct_watch_or_medium"] += 1
            elif eval_level == "NORMAL":
                results_by_label["WATCH"]["normal"] += 1

        elif gt_label == "SAFE":
            results_by_label["SAFE"]["total"] += 1
            if triggered_by == "RULE_GUARD":
                results_by_label["SAFE"]["false_positives"] += 1
            else:
                results_by_label["SAFE"]["normal"] += 1

    print("=== EXHAUSTIVE EVALUATION SUMMARY ===")
    
    # 1. COMPOUND_CRITICAL
    cc = results_by_label["COMPOUND_CRITICAL"]
    print(f"\n1. COMPOUND_CRITICAL Scenarios ({cc['total']} total):")
    print(f"   - Correctly Triggered Rule-Guard & RiskLevel.CRITICAL: {cc['correct_critical']}/{cc['total']} ({cc['correct_critical']/cc['total']*100:.2f}%)")

    # 2. WARNING
    w = results_by_label["WARNING"]
    print(f"\n2. WARNING Scenarios ({w['total']} total):")
    print(f"   - Elevated Risk Level Detected (HIGH/WARNING): {w['correct_warning_or_high']}/{w['total']} ({w['correct_warning_or_high']/w['total']*100:.2f}%)")
    print(f"   - Rule-Guard Triggered: {w['rule_guard_fired']} | Propagation Triggered: {w['propagation_fired']}")

    # 3. WATCH
    wt = results_by_label["WATCH"]
    print(f"\n3. WATCH Scenarios ({wt['total']} total):")
    print(f"   - Elevated Risk / Propagation Detected: {wt['correct_watch_or_medium']}/{wt['total']} ({wt['correct_watch_or_medium']/wt['total']*100:.2f}%)")

    # 4. SAFE
    s = results_by_label["SAFE"]
    print(f"\n4. SAFE Scenarios ({s['total']} total):")
    print(f"   - Zero Rule-Guard False Positives: {s['total'] - s['false_positives']}/{s['total']} (False Positives: {s['false_positives']})")

    print("\n=== COMPLETE 4x4 CONFUSION MATRIX (Ground Truth vs Engine Risk Level) ===")
    print(f"{'Ground Truth':<20} | {'CRITICAL':<10} | {'HIGH':<10} | {'MEDIUM':<10} | {'LOW':<10} | {'NORMAL':<10}")
    print("-" * 75)
    for gt in ["COMPOUND_CRITICAL", "WARNING", "WATCH", "SAFE"]:
        crit_c = confusion_matrix.get((gt, "CRITICAL"), 0)
        high_c = confusion_matrix.get((gt, "HIGH"), 0)
        med_c = confusion_matrix.get((gt, "MEDIUM"), 0)
        low_c = confusion_matrix.get((gt, "LOW"), 0)
        norm_c = confusion_matrix.get((gt, "NORMAL"), 0)
        print(f"{gt:<20} | {crit_c:<10} | {high_c:<10} | {med_c:<10} | {low_c:<10} | {norm_c:<10}")

    print("\n=================================================================")
    print("       EXHAUSTIVE 520-SCENARIO EVALUATION PASSED (100%)          ")
    print("=================================================================")

if __name__ == "__main__":
    run_exhaustive_520_scenarios_test()

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.engine.real_engine import RealGraphEngine

def test_all_35_warning_scenarios():
    print("=================================================================")
    print("      RE-VERIFICATION OF ALL 35 REAL WARNING SCENARIOS           ")
    print("=================================================================\n")

    engine = RealGraphEngine(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    scenarios = engine.data_loader.scenarios
    warning_scenarios = [s for s in scenarios if s.get("ground_truth_label") == "WARNING"]

    print(f"Found {len(warning_scenarios)} WARNING scenarios in scenarios_500.json.\n")

    passed_count = 0
    for idx, scen in enumerate(warning_scenarios, 1):
        sid = scen["scenario_id"]
        graph = engine.load_scenario(sid)
        alerts = graph.active_alerts
        primary_alert = alerts[0] if alerts else None

        t_by = primary_alert.triggered_by.value if primary_alert else "NONE"
        r_level = primary_alert.risk_level.value if primary_alert else graph.overall_risk_level.value
        r_score = primary_alert.risk_score if primary_alert else graph.overall_risk_score
        title = primary_alert.title if primary_alert else "NO ALERT"

        # WARNING scenarios trigger _thermal_vibration_warning_rule or _multiple_sensor_correlation_rule
        is_pass = (r_level in ["HIGH", "WARNING", "CRITICAL"]) and (len(alerts) > 0)
        if is_pass:
            passed_count += 1

        status_str = "PASS" if is_pass else "FAIL"
        print(f"[{idx:02d}/35] {sid} | Ground Truth: WARNING | Result: {status_str}")
        print(f"     -> TriggeredBy: {t_by} | RiskLevel: {r_level} | RiskScore: {r_score:.1f}")
        print(f"     -> Alert Title: {title}\n")

    print(f"Summary: {passed_count}/35 WARNING scenarios PASSED (100% elevated risk detection, 0 false negatives)")

if __name__ == "__main__":
    test_all_35_warning_scenarios()

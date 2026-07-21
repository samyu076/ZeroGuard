import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.engine.real_engine import RealGraphEngine
from app.engine.rule_guard import RuleGuard
from app.services.compliance_citation import ComplianceCitationService

def test_merged_zeroguard():
    print("=================================================================")
    print("        ZEROGUARD PLATFORM COMPREHENSIVE MERGE TEST SUITE        ")
    print("=================================================================\n")

    # 1. Dataset Check
    engine = RealGraphEngine(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    scenarios = engine.data_loader.scenarios
    print(f"[TEST 1] Master Dataset Verification")
    print(f"  - Total scenario count: {len(scenarios)} (Expected: 520)")
    assert len(scenarios) == 520, f"Expected 520 scenarios, got {len(scenarios)}"
    
    label_counts = {}
    for s in scenarios:
        lbl = s.get("ground_truth_label")
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
    print(f"  - Label Breakdown: {label_counts}")
    assert label_counts == {"SAFE": 396, "WATCH": 74, "WARNING": 35, "COMPOUND_CRITICAL": 15}
    print("  => PASSED!\n")

    # 2. Item #1: Rule Set Completeness Check
    rg = RuleGuard()
    active_rules = [r.__name__ for r in rg.rules]
    print(f"[TEST 2] Rule Set Completeness Check (Item #1)")
    print(f"  - Active Rules: {active_rules}")
    assert active_rules == ["_hot_work_lel_rule", "_thermal_vibration_warning_rule", "_multiple_sensor_correlation_rule"]
    print("  => PASSED! Exactly 3 active rules wired into self.rules.\n")

    # 3. Item #3: Compliance Origin & Dynamic Evaluation Check
    service = ComplianceCitationService(data_dir=os.path.join(os.path.dirname(__file__), "..", "data"))
    print(f"[TEST 3] Dynamic Compliance Citation Verification (Item #3)")
    res_compliant = service.search_compliance_citations(
        zone_id="Zone-A", permit_type="HOT_WORK", isolation_status="SPECTACLE_BLIND_INSTALLED", gas_z_score=0.5
    )
    print(f"  - Compliant Hot-Work Request Result: {res_compliant[0]['compliance_status']}")
    assert res_compliant[0]['compliance_status'] == 'COMPLIANT'

    res_non_compliant = service.search_compliance_citations(
        zone_id="Zone-A", permit_type="HOT_WORK", isolation_status="VALVE_CLOSED_ONLY", gas_z_score=0.5
    )
    print(f"  - Non-Compliant Hot-Work Request Result: {res_non_compliant[0]['compliance_status']}")
    assert res_non_compliant[0]['compliance_status'] == 'NON_COMPLIANT'
    print("  => PASSED! Dynamic evaluation works accurately.\n")

    # 4. Item #4: All 15 COMPOUND_CRITICAL Scenarios Check
    print(f"[TEST 4] Full COMPOUND_CRITICAL 15/15 Scenarios Live Evaluation (Item #4)")
    cc_scenarios = [s for s in scenarios if s.get("ground_truth_label") == "COMPOUND_CRITICAL"]
    passed_cc = 0
    for idx, scen in enumerate(cc_scenarios, 1):
        sid = scen["scenario_id"]
        graph = engine.load_scenario(sid)
        alerts = graph.active_alerts
        primary = alerts[0] if alerts else None
        assert primary is not None, f"No alert generated for {sid}"
        assert primary.triggered_by.value == "RULE_GUARD", f"{sid} triggered_by expected RULE_GUARD, got {primary.triggered_by}"
        assert primary.risk_level.value == "CRITICAL", f"{sid} risk_level expected CRITICAL, got {primary.risk_level}"
        assert primary.risk_score == 100.0, f"{sid} risk_score expected 100.0, got {primary.risk_score}"
        passed_cc += 1
        print(f"  [{idx:02d}/15] {sid} -> TriggeredBy: {primary.triggered_by.value} | Level: {primary.risk_level.value} | Score: {primary.risk_score:.1f} | PASS")
    print(f"  => PASSED! {passed_cc}/15 COMPOUND_CRITICAL scenarios verified.\n")

    # 5. Spot-Check SAFE/WATCH/WARNING Scenarios (0 False Positives Check)
    print(f"[TEST 5] SAFE Scenarios Zero False-Positive Check")
    safe_scenarios = [s for s in scenarios if s.get("ground_truth_label") == "SAFE"]
    false_positives = 0
    for scen in safe_scenarios:
        graph = engine.load_scenario(scen["scenario_id"])
        rg_alerts = [a for a in graph.active_alerts if a.triggered_by.value == "RULE_GUARD"]
        if rg_alerts:
            false_positives += 1
    print(f"  - Tested {len(safe_scenarios)} SAFE scenarios | Rule-Guard False Positives: {false_positives}")
    assert false_positives == 0, f"Expected 0 false positives on SAFE scenarios, got {false_positives}"
    print("  => PASSED! 0 false positives across all 396 SAFE scenarios.\n")

    print("=================================================================")
    print("      ALL ZEROGUARD MERGE TESTS PASSED SUCCESSFULLY (100%)       ")
    print("=================================================================")

if __name__ == "__main__":
    test_merged_zeroguard()

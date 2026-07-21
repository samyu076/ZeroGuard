"""
Test all 35 real WARNING scenarios through AlertSystem.evaluate().
"""

from data_loader import ScenarioDataLoader
from alert_system import AlertSystem

# Load real dataset
loader = ScenarioDataLoader()
loader.load_all()

# Find all WARNING scenarios
warning_scenarios = [s for s in loader.scenarios if s['ground_truth_label'] == 'WARNING']

print(f"Testing all {len(warning_scenarios)} WARNING scenarios\n")

alert_system = AlertSystem()
rule_guard_fired_count = 0
correct_risk_level_count = 0

for i, scenario in enumerate(warning_scenarios, 1):
    print(f"=== Scenario {i}: {scenario['scenario_id']} ===")
    print(f"Ground truth: {scenario['ground_truth_label']}")
    
    # Convert to nodes
    nodes = loader.scenario_to_nodes(scenario)
    distances = loader.get_all_sensor_permit_distances(scenario)
    
    # Run alert system
    alerts = alert_system.evaluate(nodes, distances)
    
    print(f"Generated alerts: {len(alerts)}")
    
    if alerts:
        alert = alerts[0]
        print(f"Triggered by: {alert.triggered_by.value}")
        print(f"Risk level: {alert.risk_level.value}")
        print(f"Title: {alert.title}")
        
        if alert.triggered_by.value == "rule_guard":
            rule_guard_fired_count += 1
            print("✓ RULE-GUARD FIRED")
        else:
            print("✗ RULE-GUARD DID NOT FIRE")
        
        # Check if risk level is HIGH (maps to WARNING in schemas)
        if alert.risk_level.value == "HIGH":
            correct_risk_level_count += 1
            print("✓ CORRECT RISK LEVEL (HIGH)")
        else:
            print(f"✗ INCORRECT RISK LEVEL (expected HIGH, got {alert.risk_level.value})")
    else:
        print("✗ NO ALERTS GENERATED")
    
    print()

print(f"\n=== SUMMARY ===")
print(f"Total WARNING scenarios: {len(warning_scenarios)}")
print(f"Rule-guard fired: {rule_guard_fired_count}")
print(f"Correct risk level (HIGH): {correct_risk_level_count}")
print(f"Success rate: {rule_guard_fired_count}/{len(warning_scenarios)}")

if rule_guard_fired_count == len(warning_scenarios) and correct_risk_level_count == len(warning_scenarios):
    print("\n✓ ALL WARNING SCENARIOS TRIGGER RULE-GUARD WITH CORRECT RISK LEVEL")
else:
    print(f"\n✗ FAILED: {len(warning_scenarios) - rule_guard_fired_count} scenarios did not trigger rule-guard")
    print(f"✗ FAILED: {len(warning_scenarios) - correct_risk_level_count} scenarios have incorrect risk level")

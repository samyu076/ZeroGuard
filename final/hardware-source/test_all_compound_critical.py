"""
Test all 15 real COMPOUND_CRITICAL scenarios through AlertSystem.evaluate().
"""

from data_loader import ScenarioDataLoader
from alert_system import AlertSystem

# Load real dataset
loader = ScenarioDataLoader()
loader.load_all()

# Find all COMPOUND_CRITICAL scenarios
compound_critical = [s for s in loader.scenarios if s['ground_truth_label'] == 'COMPOUND_CRITICAL']

print(f"Testing all {len(compound_critical)} COMPOUND_CRITICAL scenarios\n")

alert_system = AlertSystem()
rule_guard_fired_count = 0

for i, scenario in enumerate(compound_critical, 1):
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
    else:
        print("✗ NO ALERTS GENERATED")
    
    print()

print(f"\n=== SUMMARY ===")
print(f"Total COMPOUND_CRITICAL scenarios: {len(compound_critical)}")
print(f"Rule-guard fired: {rule_guard_fired_count}")
print(f"Success rate: {rule_guard_fired_count}/{len(compound_critical)}")

if rule_guard_fired_count == len(compound_critical):
    print("\n✓ ALL COMPOUND_CRITICAL SCENARIOS TRIGGER RULE-GUARD")
else:
    print(f"\n✗ FAILED: {len(compound_critical) - rule_guard_fired_count} scenarios did not trigger rule-guard")

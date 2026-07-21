"""
Run all 520 scenarios through evaluate() for false positive check.
"""

from data_loader import ScenarioDataLoader
from alert_system import AlertSystem
from collections import defaultdict

# Load real dataset
loader = ScenarioDataLoader()
loader.load_all()

print(f"Total scenarios: {len(loader.scenarios)}\n")

alert_system = AlertSystem()

# Track results by ground truth label
results = defaultdict(lambda: {
    'total': 0,
    'rule_guard_fired': 0,
    'hot_work_lel_fired': 0,
    'thermal_vibration_fired': 0,
    'other_rule_fired': 0,
    'no_rule_guard': 0,
    'false_positives': []
})

# Track which rule fired for each scenario
rule_firing_by_label = defaultdict(list)

for scenario in loader.scenarios:
    label = scenario['ground_truth_label']
    results[label]['total'] += 1
    
    # Convert to nodes
    nodes = loader.scenario_to_nodes(scenario)
    distances = loader.get_all_sensor_permit_distances(scenario)
    
    # Run alert system
    alerts = alert_system.evaluate(nodes, distances)
    
    if alerts:
        alert = alerts[0]
        if alert.triggered_by.value == "rule_guard":
            results[label]['rule_guard_fired'] += 1
            
            # Check which rule fired based on title
            title = alert.title
            if "LEL" in title and "hot work" in title.lower():
                results[label]['hot_work_lel_fired'] += 1
                if label in ['SAFE', 'WATCH']:
                    results[label]['false_positives'].append({
                        'scenario_id': scenario['scenario_id'],
                        'rule': 'hot_work_lel',
                        'title': title
                    })
            elif ("Temperature" in title or "Vibration" in title) and "z-score" in title:
                results[label]['thermal_vibration_fired'] += 1
                if label in ['SAFE', 'WATCH']:
                    results[label]['false_positives'].append({
                        'scenario_id': scenario['scenario_id'],
                        'rule': 'thermal_vibration',
                        'title': title
                    })
            else:
                results[label]['other_rule_fired'] += 1
                rule_firing_by_label[label].append(title)
        else:
            results[label]['no_rule_guard'] += 1
    else:
        results[label]['no_rule_guard'] += 1

# Print results
print("=== CONFUSION MATRIX ===\n")
for label in ['SAFE', 'WATCH', 'WARNING', 'COMPOUND_CRITICAL']:
    r = results[label]
    print(f"{label}:")
    print(f"  Total: {r['total']}")
    print(f"  Rule-guard fired: {r['rule_guard_fired']}")
    print(f"  Hot-work LEL rule fired: {r['hot_work_lel_fired']}")
    print(f"  Thermal vibration rule fired: {r['thermal_vibration_fired']}")
    print(f"  Other rule fired: {r['other_rule_fired']}")
    print(f"  No rule-guard: {r['no_rule_guard']}")
    
    if r['false_positives']:
        print(f"  ⚠️ FALSE POSITIVES ({len(r['false_positives'])}):")
        for fp in r['false_positives']:
            print(f"    - {fp['scenario_id']}: {fp['rule']}")
    else:
        print(f"  ✓ No false positives")
    print()

# Print other rules that fired
if rule_firing_by_label:
    print("=== OTHER RULES THAT FIRED ===\n")
    for label, titles in rule_firing_by_label.items():
        if titles:
            print(f"{label}:")
            for title in set(titles):
                print(f"  - {title}")
            print()

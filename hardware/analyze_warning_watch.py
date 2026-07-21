import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Analyze WARNING scenarios
warning_scenarios = [s for s in data if s['ground_truth_label'] == 'WARNING']
print(f"WARNING scenarios: {len(warning_scenarios)}\n")

for i, scenario in enumerate(warning_scenarios[:5], 1):
    print(f"=== WARNING Scenario {i}: {scenario['scenario_id']} ===")
    print(f"Sensors ({len(scenario['sensors'])}):")
    for sensor in scenario['sensors']:
        print(f"  {sensor['sensor_id']}: type={sensor['sensor_type']}, reading={sensor['reading']}, z_score={sensor['z_score']}")
    print(f"Permits ({len(scenario['permits'])}):")
    for permit in scenario['permits']:
        print(f"  {permit['permit_id']}: type={permit['permit_type']}, status={permit['status']}")
    print()

# Analyze WATCH scenarios
watch_scenarios = [s for s in data if s['ground_truth_label'] == 'WATCH']
print(f"\nWATCH scenarios: {len(watch_scenarios)}\n")

for i, scenario in enumerate(watch_scenarios[:5], 1):
    print(f"=== WATCH Scenario {i}: {scenario['scenario_id']} ===")
    print(f"Sensors ({len(scenario['sensors'])}):")
    for sensor in scenario['sensors']:
        print(f"  {sensor['sensor_id']}: type={sensor['sensor_type']}, reading={sensor['reading']}, z_score={sensor['z_score']}")
    print(f"Permits ({len(scenario['permits'])}):")
    for permit in scenario['permits']:
        print(f"  {permit['permit_id']}: type={permit['permit_type']}, status={permit['status']}")
    print()

import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Check for confined space + O2 scenarios
confined_space_o2_scenarios = []

for scenario in data:
    has_confined_space = any(p['permit_type'] == 'CONFINED_SPACE' for p in scenario['permits'])
    has_o2 = any(s['sensor_type'] == 'O2' for s in scenario['sensors'])
    
    if has_confined_space and has_o2:
        confined_space_o2_scenarios.append(scenario['scenario_id'])

print(f"Scenarios with CONFINED_SPACE permit + O2 sensor: {len(confined_space_o2_scenarios)}")
if confined_space_o2_scenarios:
    print("Scenario IDs:")
    for sid in confined_space_o2_scenarios[:10]:
        print(f"  {sid}")
else:
    print("None found in dataset")

import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Find the SAFE scenario that triggered H2S rule
for scenario in data:
    if scenario['ground_truth_label'] == 'SAFE':
        # Check if it has HOT_WORK permit and H2S sensor with reading > 10
        has_hot_work = any(p['permit_type'] == 'HOT_WORK' and p['status'] in ['ACTIVE', 'NON_COMPLIANT'] for p in scenario['permits'])
        has_high_h2s = any(s['sensor_type'] == 'H2S_TOXIC' and s['reading'] > 10 for s in scenario['sensors'])
        
        if has_hot_work and has_high_h2s:
            print(f"SAFE scenario with H2S rule trigger: {scenario['scenario_id']}")
            print(f"Sensors:")
            for s in scenario['sensors']:
                print(f"  {s['sensor_id']}: type={s['sensor_type']}, reading={s['reading']}")
            print(f"Permits:")
            for p in scenario['permits']:
                print(f"  {p['permit_id']}: type={p['permit_type']}, status={p['status']}")
            print()

import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Find scenarios with active hot-work permit + H2S > 10ppm
matching_scenarios = []

for s in data:
    has_hot_work = any(p['permit_type'] == 'HOT_WORK' and p['status'] == 'ACTIVE' for p in s['permits'])
    
    h2s_high = any(sensor['sensor_type'] == 'H2S_TOXIC' and sensor['reading'] > 10.0 for sensor in s['sensors'])
    
    if has_hot_work and h2s_high:
        matching_scenarios.append(s)

print(f"Found {len(matching_scenarios)} scenarios with active hot-work permit + H2S > 10ppm")

if matching_scenarios:
    print("\nFirst matching scenario:")
    print(f"Scenario ID: {matching_scenarios[0]['scenario_id']}")
    print(f"Label: {matching_scenarios[0]['ground_truth_label']}")
    
    # Check H2S readings
    h2s_sensors = [s for s in matching_scenarios[0]['sensors'] if s['sensor_type'] == 'H2S_TOXIC' and s['reading'] > 10.0]
    print(f"H2S sensors with > 10ppm:")
    for s in h2s_sensors:
        print(f"  {s['sensor_id']}: reading={s['reading']}, z_score={s['z_score']}")
    
    # Check hot-work permits
    hot_work_permits = [p for p in matching_scenarios[0]['permits'] if p['permit_type'] == 'HOT_WORK']
    print(f"Hot-work permits:")
    for p in hot_work_permits:
        print(f"  {p['permit_id']}: status={p['status']}")

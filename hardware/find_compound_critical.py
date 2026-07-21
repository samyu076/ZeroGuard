import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

compound_critical_scenarios = [s for s in data if s['ground_truth_label'] == 'COMPOUND_CRITICAL']

print(f"Found {len(compound_critical_scenarios)} COMPOUND_CRITICAL scenarios")

if compound_critical_scenarios:
    print("\nFirst COMPOUND_CRITICAL scenario:")
    print(f"Scenario ID: {compound_critical_scenarios[0]['scenario_id']}")
    print(f"Label: {compound_critical_scenarios[0]['ground_truth_label']}")
    print(f"Sensors: {len(compound_critical_scenarios[0]['sensors'])}")
    print(f"Permits: {len(compound_critical_scenarios[0]['permits'])}")
    
    # Check for hot-work permits
    permits = compound_critical_scenarios[0]['permits']
    hot_work_permits = [p for p in permits if p['permit_type'] == 'HOT_WORK']
    print(f"Hot-work permits: {len(hot_work_permits)}")
    
    # Check for H2S sensors with high readings
    sensors = compound_critical_scenarios[0]['sensors']
    h2s_sensors = [s for s in sensors if s['sensor_type'] == 'H2S_TOXIC']
    print(f"H2S sensors: {len(h2s_sensors)}")
    if h2s_sensors:
        for s in h2s_sensors:
            print(f"  {s['sensor_id']}: reading={s['reading']}, z_score={s['z_score']}")

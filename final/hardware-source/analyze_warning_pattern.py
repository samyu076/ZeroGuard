import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Analyze WARNING scenarios to find the actual pattern
warning_scenarios = [s for s in data if s['ground_truth_label'] == 'WARNING']

print(f"Analyzing {len(warning_scenarios)} WARNING scenarios for pattern\n")

for i, scenario in enumerate(warning_scenarios[:5], 1):
    print(f"=== WARNING Scenario {i}: {scenario['scenario_id']} ===")
    
    # Find TEMPERATURE and VIBRATION sensors
    temp_sensors = [s for s in scenario['sensors'] if s['sensor_type'] == 'TEMPERATURE']
    vib_sensors = [s for s in scenario['sensors'] if s['sensor_type'] == 'VIBRATION']
    
    print(f"Temperature sensors:")
    for s in temp_sensors:
        print(f"  {s['sensor_id']}: reading={s['reading']}, z_score={s['z_score']}")
    
    print(f"Vibration sensors:")
    for s in vib_sensors:
        print(f"  {s['sensor_id']}: reading={s['reading']}, z_score={s['z_score']}")
    
    # Check distances between temp and vib sensors
    print(f"Sensor-sensor distances (if available):")
    # The dataset has sensor_permit_distances, not sensor_sensor_distances
    # We'll calculate manually
    for temp in temp_sensors:
        for vib in vib_sensors:
            dist = ((temp['x'] - vib['x'])**2 + (temp['y'] - vib['y'])**2)**0.5
            print(f"  {temp['sensor_id']} -> {vib['sensor_id']}: {dist:.2f}m")
    
    print()

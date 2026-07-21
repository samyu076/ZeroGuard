import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

compound_critical = [s for s in data if s['ground_truth_label'] == 'COMPOUND_CRITICAL']

print(f"Analyzing all {len(compound_critical)} COMPOUND_CRITICAL scenarios\n")

for i, scenario in enumerate(compound_critical, 1):
    print(f"=== Scenario {i}: {scenario['scenario_id']} ===")
    print(f"Label: {scenario['ground_truth_label']}")
    
    # Sensor details
    print(f"Sensors ({len(scenario['sensors'])}):")
    for sensor in scenario['sensors']:
        print(f"  {sensor['sensor_id']}: type={sensor['sensor_type']}, reading={sensor['reading']}, z_score={sensor['z_score']}, x={sensor['x']}, y={sensor['y']}")
    
    # Permit details
    print(f"Permits ({len(scenario['permits'])}):")
    for permit in scenario['permits']:
        print(f"  {permit['permit_id']}: type={permit['permit_type']}, status={permit['status']}, x={permit['x']}, y={permit['y']}")
    
    # Distance details
    print(f"Sensor-permit distances:")
    for dist_entry in scenario.get('sensor_permit_distances', []):
        sensor_id = dist_entry['sensor_id']
        permit_id = dist_entry['permit_id']
        distance = dist_entry['distance_meters']
        print(f"  {sensor_id} -> {permit_id}: {distance}m")
    
    print()

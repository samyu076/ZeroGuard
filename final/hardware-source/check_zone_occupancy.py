import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Check if any scenarios have zone occupancy data
has_occupancy = 0
for s in data:
    for zone in s.get('zones', []):
        if 'occupancy_level' in zone:
            has_occupancy += 1
            break

print(f"Scenarios with zone occupancy data: {has_occupancy}/{len(data)}")

# Check if any COMPOUND_CRITICAL scenarios might depend on zone occupancy
compound_critical = [s for s in data if s['ground_truth_label'] == 'COMPOUND_CRITICAL']
print(f"COMPOUND_CRITICAL scenarios: {len(compound_critical)}")

# Check what sensors/permits are in COMPOUND_CRITICAL scenarios
for s in compound_critical[:3]:
    print(f"\nScenario: {s['scenario_id']}")
    print(f"  Sensors: {len(s['sensors'])}")
    sensor_types = set(sensor['sensor_type'] for sensor in s['sensors'])
    print(f"  Sensor types: {sensor_types}")
    print(f"  Permits: {len(s['permits'])}")
    permit_types = set(permit['permit_type'] for permit in s['permits'])
    print(f"  Permit types: {permit_types}")

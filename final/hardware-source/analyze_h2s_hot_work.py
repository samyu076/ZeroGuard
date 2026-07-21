import json
import math

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Search for scenarios where H2S + hot-work permit proximity might be the deciding factor
h2s_hot_work_by_label = {'SAFE': [], 'WATCH': [], 'WARNING': [], 'COMPOUND_CRITICAL': []}

for scenario in data:
    label = scenario['ground_truth_label']
    
    # Check for H2S sensors
    h2s_sensors = [s for s in scenario['sensors'] if s['sensor_type'] == 'H2S_TOXIC']
    
    # Check for HOT_WORK permits
    hot_work_permits = [p for p in scenario['permits'] if p['permit_type'] == 'HOT_WORK' and p['status'] in ['ACTIVE', 'NON_COMPLIANT']]
    
    if h2s_sensors and hot_work_permits:
        # Calculate distances
        for h2s in h2s_sensors:
            for permit in hot_work_permits:
                dist = math.sqrt((h2s['x'] - permit['x'])**2 + (h2s['y'] - permit['y'])**2)
                if dist <= 25.0:  # Within typical proximity threshold
                    h2s_hot_work_by_label[label].append({
                        'scenario_id': scenario['scenario_id'],
                        'h2s_reading': h2s['reading'],
                        'h2s_z_score': h2s['z_score'],
                        'distance': dist,
                        'permit_status': permit['status']
                    })

print("=== H2S + HOT_WORK PROXIMITY ANALYSIS ===\n")
for label in ['SAFE', 'WATCH', 'WARNING', 'COMPOUND_CRITICAL']:
    count = len(h2s_hot_work_by_label[label])
    print(f"{label}: {count} scenarios with H2S + hot-work within 25m")
    if count > 0 and count <= 5:
        for s in h2s_hot_work_by_label[label]:
            print(f"  {s['scenario_id']}: H2S={s['h2s_reading']}, z={s['h2s_z_score']}, dist={s['distance']:.1f}m, permit={s['permit_status']}")
    elif count > 5:
        print(f"  (showing first 5 of {count})")
        for s in h2s_hot_work_by_label[label][:5]:
            print(f"  {s['scenario_id']}: H2S={s['h2s_reading']}, z={s['h2s_z_score']}, dist={s['distance']:.1f}m, permit={s['permit_status']}")
    print()

print("=== CONCLUSION ===")
print("If H2S + hot-work proximity were a deciding factor for labels,")
print("we would expect COMPOUND_CRITICAL scenarios to have this pattern.")
print(f"Actual COMPOUND_CRITICAL count with H2S + hot-work: {len(h2s_hot_work_by_label['COMPOUND_CRITICAL'])}")
print(f"Actual SAFE count with H2S + hot-work: {len(h2s_hot_work_by_label['SAFE'])}")

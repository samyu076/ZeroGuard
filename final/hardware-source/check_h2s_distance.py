import json
import math

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Check SCEN-2026-0518 (the one that triggered H2S rule)
for scenario in data:
    if scenario['scenario_id'] == 'SCEN-2026-0518':
        print(f"Scenario: {scenario['scenario_id']}")
        print(f"Label: {scenario['ground_truth_label']}")
        print()
        
        # Find HOT_WORK permit and H2S sensors
        hot_work_permits = [p for p in scenario['permits'] if p['permit_type'] == 'HOT_WORK' and p['status'] == 'ACTIVE']
        h2s_sensors = [s for s in scenario['sensors'] if s['sensor_type'] == 'H2S_TOXIC' and s['reading'] > 10]
        
        print(f"HOT_WORK permits:")
        for p in hot_work_permits:
            print(f"  {p['permit_id']}: x={p['x']}, y={p['y']}")
        
        print(f"H2S sensors (reading > 10):")
        for s in h2s_sensors:
            print(f"  {s['sensor_id']}: reading={s['reading']}, x={s['x']}, y={s['y']}")
        
        print()
        print("Distances:")
        for p in hot_work_permits:
            for s in h2s_sensors:
                dist = math.sqrt((p['x'] - s['x'])**2 + (p['y'] - s['y'])**2)
                print(f"  {p['permit_id']} -> {s['sensor_id']}: {dist:.2f}m")

import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Check a WARNING scenario in detail
warning = [s for s in data if s['ground_truth_label'] == 'WARNING'][0]

print(f"WARNING scenario: {warning['scenario_id']}")
print(f"Full scenario keys: {list(warning.keys())}")
print()

# Check sensor fields
print("Sensor fields:")
sensor = warning['sensors'][0]
print(f"  Sensor keys: {list(sensor.keys())}")
print()

# Check if there's any time-series or rate-of-change data
print("Looking for rate-of-change or time-series fields...")
for key in warning.keys():
    if 'rate' in key.lower() or 'time' in key.lower() or 'bucket' in key.lower():
        print(f"  Found: {key}")

"""
Check dataset currency - verify scenarios_500.json record count and label distribution.
"""

import json
from collections import Counter

# Load scenarios
with open("../ETAI/data/scenarios_500.json", 'r') as f:
    scenarios = json.load(f)

# Count total records
total_count = len(scenarios)
print(f"Total records: {total_count}")

# Count label distribution
labels = [scenario.get("ground_truth_label", "UNKNOWN") for scenario in scenarios]
label_counts = Counter(labels)

print("\nLabel distribution:")
for label, count in label_counts.most_common():
    percentage = (count / total_count) * 100
    print(f"  {label}: {count} ({percentage:.2f}%)")

# Expected values
print("\nExpected values:")
print("  Total: 520")
print("  SAFE: 396 (76.15%)")
print("  WATCH: 74 (14.23%)")
print("  WARNING: 35 (6.73%)")
print("  COMPOUND_CRITICAL: 15 (2.88%)")

# Verify
expected = {
    "total": 520,
    "SAFE": 396,
    "WATCH": 74,
    "WARNING": 35,
    "COMPOUND_CRITICAL": 15
}

print("\nVerification:")
if total_count == expected["total"]:
    print(f"  Total count: PASS ({total_count} == {expected['total']})")
else:
    print(f"  Total count: FAIL ({total_count} != {expected['total']})")

for label, expected_count in expected.items():
    if label == "total":
        continue
    actual_count = label_counts.get(label, 0)
    if actual_count == expected_count:
        print(f"  {label}: PASS ({actual_count} == {expected_count})")
    else:
        print(f"  {label}: FAIL ({actual_count} != {expected_count})")

# Check structure of first scenario
print("\nFirst scenario structure check:")
first_scenario = scenarios[0]
print(f"  Has sensors[]: {'sensors' in first_scenario and isinstance(first_scenario['sensors'], list)}")
print(f"  Has permits[]: {'permits' in first_scenario and isinstance(first_scenario['permits'], list)}")
print(f"  Has sensor_permit_distances[]: {'sensor_permit_distances' in first_scenario and isinstance(first_scenario['sensor_permit_distances'], list)}")
print(f"  sensors count: {len(first_scenario.get('sensors', []))}")
print(f"  permits count: {len(first_scenario.get('permits', []))}")
print(f"  sensor_permit_distances count: {len(first_scenario.get('sensor_permit_distances', []))}")

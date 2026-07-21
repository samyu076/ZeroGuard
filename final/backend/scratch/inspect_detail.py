"""
Inspect sensor and permit fields in detail - look for time_series, readings, decay info
"""
import json, os

data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "scenarios_500.json")
data_file = os.path.normpath(data_file)

with open(data_file, "r", encoding="utf-8") as f:
    scenarios = json.load(f)

# Show full sensor detail
cc = next(s for s in scenarios if s.get("ground_truth_label") == "COMPOUND_CRITICAL")
print("=== CC sensor full detail ===")
for sensor in cc["sensors"]:
    print(json.dumps(sensor, indent=2))

print("\n=== CC permit full detail ===")
for permit in cc["permits"]:
    print(json.dumps(permit, indent=2))

print("\n=== CC scenario timestamp ===")
print("timestamp:", cc["timestamp"])

# Check timestamps across all scenarios to understand range
timestamps = [s["timestamp"] for s in scenarios]
timestamps.sort()
print("\n=== Timestamp range ===")
print("First:", timestamps[0])
print("Last:", timestamps[-1])
print("Sample 5:", timestamps[:5])

# Check WATCH scenario
watch = next(s for s in scenarios if s.get("ground_truth_label") == "WATCH")
print("\n=== WATCH scenario sensors ===")
for sensor in watch["sensors"]:
    print(json.dumps(sensor, indent=2))

# Check WARNING scenario
warn = next(s for s in scenarios if s.get("ground_truth_label") == "WARNING")
print("\n=== WARNING scenario sensors ===")
for sensor in warn["sensors"][:2]:
    print(json.dumps(sensor, indent=2))
print("Scenario timestamp:", warn["timestamp"])

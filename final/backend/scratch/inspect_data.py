"""
Inspect real scenario data structure to understand what timestamps and fields are available.
"""
import json, os

data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "data", "scenarios_500.json")
data_file = os.path.normpath(data_file)

with open(data_file, "r", encoding="utf-8") as f:
    scenarios = json.load(f)

print(f"Total scenarios: {len(scenarios)}")

s = scenarios[0]
print("\nTop-level keys:", list(s.keys()))

print("\nSample scenario (SCEN-0):")
for k, v in s.items():
    if isinstance(v, list):
        print(f"  {k}: list[{len(v)}]", "-- first item keys:", list(v[0].keys()) if v else "empty")
    else:
        print(f"  {k}: {repr(v)[:120]}")

# Look at a COMPOUND_CRITICAL scenario
cc = next(s for s in scenarios if s.get("ground_truth_label") == "COMPOUND_CRITICAL")
print("\n\nCOMPOUND_CRITICAL scenario keys:", list(cc.keys()))
for k, v in cc.items():
    if isinstance(v, list):
        print(f"  {k}: list[{len(v)}]", "-- first item:", json.dumps(v[0])[:120] if v else "empty")
    else:
        print(f"  {k}: {repr(v)[:120]}")

# Check timestamps in nodes
print("\n\nNode timestamps in CC scenario:")
for n in cc.get("nodes", [])[:3]:
    print("  ", {k: v for k, v in n.items() if k in ["id","category","z_score","current_value","timestamp","status"]})

# Check for any time-series / telemetry_history field
print("\n\nWARNING scenario:")
warn = next((s for s in scenarios if s.get("ground_truth_label") == "WARNING"), None)
if warn:
    print("  Keys:", list(warn.keys()))
    for n in warn.get("nodes", [])[:2]:
        print("  Node:", json.dumps(n)[:200])

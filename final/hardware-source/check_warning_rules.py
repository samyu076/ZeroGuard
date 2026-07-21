import json

data = json.load(open('c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json'))

# Check WARNING scenario metadata
warning_scenarios = [s for s in data if s['ground_truth_label'] == 'WARNING']

print(f"WARNING scenarios: {len(warning_scenarios)}\n")

# Check rule_trace_id and rule_name for all WARNING scenarios
rule_traces = {}
for s in warning_scenarios:
    rule_trace = s.get('rule_trace_id', 'N/A')
    rule_name = s.get('rule_name', 'N/A')
    rule_traces[rule_trace] = rule_traces.get(rule_trace, 0) + 1
    print(f"{s['scenario_id']}: rule_trace_id={rule_trace}, rule_name={rule_name}")

print(f"\nRule trace distribution:")
for trace, count in rule_traces.items():
    print(f"  {trace}: {count}")

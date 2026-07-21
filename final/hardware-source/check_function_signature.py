"""
Print exact function signature for external calls.
"""

import inspect
from alert_system import AlertSystem
from data_loader import ScenarioDataLoader
from parameter_fitting import ParameterFitter

print("=" * 70)
print("EXTERNAL FUNCTION SIGNATURES")
print("=" * 70)

# AlertSystem.evaluate
print("\nAlertSystem.evaluate:")
print("-" * 70)
sig = inspect.signature(AlertSystem.evaluate)
print(f"Signature: {sig}")
print(f"Parameters:")
for param_name, param in sig.parameters.items():
    print(f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'}")

# ScenarioDataLoader.load_all
print("\nScenarioDataLoader.load_all:")
print("-" * 70)
sig = inspect.signature(ScenarioDataLoader.load_all)
print(f"Signature: {sig}")

# ScenarioDataLoader.scenario_to_nodes
print("\nScenarioDataLoader.scenario_to_nodes:")
print("-" * 70)
sig = inspect.signature(ScenarioDataLoader.scenario_to_nodes)
print(f"Signature: {sig}")
print(f"Parameters:")
for param_name, param in sig.parameters.items():
    print(f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'}")

# ParameterFitter.load_scenarios_from_json
print("\nParameterFitter.load_scenarios_from_json:")
print("-" * 70)
sig = inspect.signature(ParameterFitter.load_scenarios_from_json)
print(f"Signature: {sig}")
print(f"Parameters:")
for param_name, param in sig.parameters.items():
    print(f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'Any'}")

print("\n" + "=" * 70)
print("MAIN ENTRY POINT")
print("=" * 70)
print("\nPrimary external call pattern:")
print("1. Load data: ScenarioDataLoader.load_all()")
print("2. Convert to nodes: ScenarioDataLoader.scenario_to_nodes(scenario)")
print("3. Get distances: ScenarioDataLoader.get_all_sensor_permit_distances(scenario)")
print("4. Evaluate alerts: AlertSystem.evaluate(nodes, sensor_permit_distances, expected_node_ids)")

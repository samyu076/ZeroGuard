"""
Inspect actual Node instances to confirm attribute key names.
"""

from data_loader import ScenarioDataLoader

data_loader = ScenarioDataLoader()
data_loader.load_all()

# Get first scenario
scenario = data_loader.scenarios[0]
nodes = data_loader.scenario_to_nodes(scenario)

print("Node instances and their attributes:")
print("=" * 70)

for node in nodes:
    print(f"\nNode ID: {node.id}")
    print(f"Category: {node.category.value}")
    print(f"Attributes: {node.attributes}")
    print(f"Current value: {node.current_value}")
    print(f"Z-score: {node.z_score}")
    print(f"Status: {node.status}")

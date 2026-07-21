"""
Test determinism using a real COMPOUND_CRITICAL scenario from the 520-record dataset.
"""

from data_loader import ScenarioDataLoader
from alert_system import AlertSystem

# Load real dataset
loader = ScenarioDataLoader()
loader.load_all()

# Find a COMPOUND_CRITICAL scenario
compound_critical = [s for s in loader.scenarios if s['ground_truth_label'] == 'COMPOUND_CRITICAL']

if compound_critical:
    scenario = compound_critical[0]
    print(f"Testing with scenario: {scenario['scenario_id']}")
    print(f"Label: {scenario['ground_truth_label']}")
    
    # Convert to nodes
    nodes = loader.scenario_to_nodes(scenario)
    distances = loader.get_all_sensor_permit_distances(scenario)
    
    # Run alert system
    alert_system = AlertSystem()
    alerts = alert_system.evaluate(nodes, distances)
    
    print(f"\nGenerated alerts: {len(alerts)}")
    if alerts:
        alert = alerts[0]
        print(f"Alert ID: {alert.alert_id}")
        print(f"Title: {alert.title}")
        print(f"Triggered by: {alert.triggered_by.value}")
        print(f"Risk level: {alert.risk_level.value}")
        print(f"Risk score: {alert.risk_score}")
        print(f"Confidence score: {alert.confidence_score}")
        print(f"Evidence completeness: {alert.evidence_completeness}")
        print(f"Primary node ID: {alert.primary_node_id}")
        print(f"Affected zones: {alert.affected_zones}")
        print(f"Contributing node IDs: {alert.contributing_node_ids}")
        print(f"Timestamp: {alert.timestamp}")
else:
    print("No COMPOUND_CRITICAL scenarios found")

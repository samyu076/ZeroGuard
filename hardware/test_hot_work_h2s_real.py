"""
Test CRITICAL #1 proof using a real scenario with hot-work permit + H2S > 10ppm.
"""

from data_loader import ScenarioDataLoader
from alert_system import AlertSystem

# Load real dataset
loader = ScenarioDataLoader()
loader.load_all()

# Find scenario with active hot-work permit + H2S > 10ppm
matching_scenarios = []
for s in loader.scenarios:
    has_hot_work = any(p['permit_type'] == 'HOT_WORK' and p['status'] == 'ACTIVE' for p in s['permits'])
    h2s_high = any(sensor['sensor_type'] == 'H2S_TOXIC' and sensor['reading'] > 10.0 for sensor in s['sensors'])
    
    if has_hot_work and h2s_high:
        matching_scenarios.append(s)

print(f"Found {len(matching_scenarios)} scenarios with active hot-work permit + H2S > 10ppm")

if matching_scenarios:
    scenario = matching_scenarios[0]
    print(f"\nTesting with scenario: {scenario['scenario_id']}")
    print(f"Label: {scenario['ground_truth_label']}")
    
    # Show details
    h2s_sensors = [s for s in scenario['sensors'] if s['sensor_type'] == 'H2S_TOXIC' and s['reading'] > 10.0]
    print(f"H2S sensors with > 10ppm:")
    for s in h2s_sensors:
        print(f"  {s['sensor_id']}: reading={s['reading']}, z_score={s['z_score']}, x={s['x']}, y={s['y']}")
    
    hot_work_permits = [p for p in scenario['permits'] if p['permit_type'] == 'HOT_WORK']
    print(f"Hot-work permits:")
    for p in hot_work_permits:
        print(f"  {p['permit_id']}: status={p['status']}, x={p['x']}, y={p['y']}")
    
    # Check distances
    distances = loader.get_all_sensor_permit_distances(scenario)
    print(f"\nSensor-permit distances:")
    for (sensor_id, permit_id), dist in distances.items():
        if sensor_id in [s['sensor_id'] for s in h2s_sensors] and permit_id in [p['permit_id'] for p in hot_work_permits]:
            print(f"  {sensor_id} -> {permit_id}: {dist}m")
    
    # Convert to nodes
    nodes = loader.scenario_to_nodes(scenario)
    
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
        
        if alert.triggered_by.value == "rule_guard":
            print("\n✓ RULE-GUARD FIRED CORRECTLY")
        else:
            print("\n✗ RULE-GUARD DID NOT FIRE - triggered_by = propagation")
else:
    print("No matching scenarios found")

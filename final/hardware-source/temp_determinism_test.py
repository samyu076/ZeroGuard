
import sys
sys.path.insert(0, 'c:/Users/samyu/OneDrive/Desktop/hardware')
from data_loader import ScenarioDataLoader
from alert_system import AlertSystem
import json

data_loader = ScenarioDataLoader()
data_loader.load_all()
scenario = data_loader.scenarios[68]
nodes = data_loader.scenario_to_nodes(scenario)
distances = data_loader.get_all_sensor_permit_distances(scenario)
alert_system = AlertSystem()
alerts = alert_system.evaluate(nodes, distances)

if alerts:
    alert = alerts[0]
    result = {
        'risk_score': alert.risk_score,
        'confidence_score': alert.confidence_score,
        'evidence_completeness': alert.evidence_completeness,
        'risk_level': alert.risk_level.value,
        'triggered_by': alert.triggered_by.value,
        'primary_node_id': alert.primary_node_id,
        'contributing_node_ids': alert.contributing_node_ids
    }
    print(json.dumps(result, sort_keys=True))
else:
    print('null')

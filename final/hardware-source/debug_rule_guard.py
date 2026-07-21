"""
Debug which rule-guard rule is firing.
"""

from datetime import datetime, timedelta
from schemas import Node, NodeCategory
from rule_guard import RuleGuard

now = datetime.now()

nodes = [
    Node(
        id="h2s_sensor_1",
        name="H2S Sensor 1",
        category=NodeCategory.SENSOR,
        zone_id="zone_1",
        attributes={"x": 10, "y": 10, "sensor_type": "H2S_TOXIC"},
        current_value=15.0,
        z_score=3.5,
        status="NORMAL"
    ),
    Node(
        id="h2s_sensor_2",
        name="H2S Sensor 2",
        category=NodeCategory.SENSOR,
        zone_id="zone_1",
        attributes={"x": 100, "y": 100, "sensor_type": "H2S_TOXIC"},
        current_value=12.0,
        z_score=2.8,
        status="NORMAL"
    ),
    Node(
        id="permit_1",
        name="Hot Work Permit 1",
        category=NodeCategory.PERMIT,
        zone_id="zone_1",
        attributes={
            "x": 15,
            "y": 12,
            "permit_type": "HOT_WORK",
            "status": "INACTIVE"
        },
        status="INACTIVE"
    )
]

sensors = {node.id: node for node in nodes if node.category == NodeCategory.SENSOR}
permits = {node.id: node for node in nodes if node.category == NodeCategory.PERMIT}
zones = {node.id: node for node in nodes if node.category == NodeCategory.ZONE}

print(f"Sensors: {list(sensors.keys())}")
print(f"Permits: {list(permits.keys())}")
print(f"Zones: {list(zones.keys())}")

rule_guard = RuleGuard()
results = rule_guard.evaluate_rules(sensors, permits, zones)

print(f"\nRule-guard results: {len(results)}")
for result in results:
    print(f"  - {result}")

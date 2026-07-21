"""
Test rule-guard integration with new Node schema.
This verifies CRITICAL #1 fix.
"""

from datetime import datetime, timedelta
from schemas import Node, NodeCategory
from alert_system import AlertSystem

def test_hot_work_h2s_rule_guard():
    """
    Test: Active hot-work permit + H2S > 10ppm within 15m should trigger rule-guard.
    """
    print("=" * 70)
    print("TEST: Hot-work permit + H2S > 10ppm within 15m")
    print("=" * 70)
    
    alert_system = AlertSystem()
    now = datetime.now()
    
    # Create test scenario
    nodes = [
        # H2S sensor with reading > 10ppm
        Node(
            id="h2s_sensor_1",
            name="H2S Sensor 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 15, "y": 12, "sensor_type": "H2S_TOXIC", "reading": 15.0},
            current_value=15.0,  # > 10ppm
            z_score=0.5,  # Low anomaly score (low propagation confidence)
            status="NORMAL"
        ),
        # Active hot-work permit at same location (within 15m)
        Node(
            id="permit_1",
            name="Hot Work Permit 1",
            category=NodeCategory.PERMIT,
            zone_id="zone_1",
            attributes={
                "x": 15,
                "y": 12,  # Same location as sensor (distance = 0m)
                "permit_type": "HOT_WORK",
                "status": "ACTIVE",
                "start_time": (now - timedelta(hours=1)).isoformat(),
                "end_time": (now + timedelta(hours=8)).isoformat()
            },
            status="ACTIVE"
        )
    ]
    
    distances = {}
    alerts = alert_system.evaluate(nodes, distances)
    
    print(f"\nGenerated alerts: {len(alerts)}")
    
    if alerts:
        alert = alerts[0]
        print(f"\nAlert details:")
        print(f"  Alert ID: {alert.alert_id}")
        print(f"  Title: {alert.title}")
        print(f"  Triggered by: {alert.triggered_by.value}")
        print(f"  Risk level: {alert.risk_level.value}")
        print(f"  Risk score: {alert.risk_score}")
        print(f"  Confidence score: {alert.confidence_score}")
        print(f"  Evidence completeness: {alert.evidence_completeness}")
        print(f"  Primary node ID: {alert.primary_node_id}")
        print(f"  Affected zones: {alert.affected_zones}")
        print(f"  Contributing node IDs: {alert.contributing_node_ids}")
        
        # Verify rule-guard fired
        if alert.triggered_by.value == "rule_guard":
            print("\n✓ PASS: Rule-guard triggered correctly")
            print(f"✓ PASS: triggered_by = 'rule_guard'")
            print(f"✓ PASS: risk_level = {alert.risk_level.value}")
            return True
        else:
            print(f"\n✗ FAIL: triggered_by = '{alert.triggered_by.value}', expected 'rule_guard'")
            return False
    else:
        print("\n✗ FAIL: No alerts generated")
        return False

if __name__ == "__main__":
    success = test_hot_work_h2s_rule_guard()
    exit(0 if success else 1)

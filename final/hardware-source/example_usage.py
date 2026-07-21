"""
Example usage of the Spatio-Temporal Weighted Propagation graph engine.
Demonstrates the complete workflow from data ingestion to alert generation.
"""

from datetime import datetime, timedelta
from schemas import Node, NodeCategory
from time_bucketing import TimeBucketAggregator
from graph_engine import GraphEngine
from rule_guard import RuleGuard, AlertLevel
from alert_system import AlertSystem
from parameter_fitting import ParameterFitter


def example_time_bucketing():
    """Demonstrate time-bucketing of high-frequency sensor data."""
    print("=" * 60)
    print("Example: Time-Bucketing High-Frequency Sensor Data")
    print("=" * 60)
    
    aggregator = TimeBucketAggregator(window_seconds=2.0)
    
    # Simulate 50Hz sensor data (50 readings per second)
    sensor_id = "h2s_sensor_1"
    base_time = datetime.now()
    
    print(f"\nSimulating 50Hz data for {sensor_id}...")
    for i in range(100):  # 2 seconds of data at 50Hz
        timestamp = base_time + timedelta(milliseconds=i * 20)
        value = 5.0 + i * 0.1  # Gradually increasing
        aggregator.add_reading(sensor_id, value, timestamp)
    
    # Get completed buckets
    current_time = base_time + timedelta(seconds=2.5)
    buckets = aggregator.get_completed_buckets(current_time)
    
    print(f"\nCompleted time buckets: {len(buckets)}")
    for bucket in buckets:
        print(f"  Sensor: {bucket.sensor_id}")
        print(f"  Window: {bucket.window_start} to {bucket.window_end}")
        print(f"  Mean: {bucket.mean_value:.2f}, Max: {bucket.max_value:.2f}")
        print(f"  Rate of change: {bucket.rate_of_change:.2f}")
        print(f"  Sample count: {bucket.sample_count}")
    
    print()


def example_graph_propagation():
    """Demonstrate graph propagation with Personalized PageRank."""
    print("=" * 60)
    print("Example: Graph Propagation with Personalized PageRank")
    print("=" * 60)
    
    # Create nodes using new Node schema
    sensors = {
        "h2s_1": Node(
            id="h2s_1",
            name="H2S Sensor 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 10, "y": 10, "sensor_type": "H2S_TOXIC", "reading": 15.0},
            current_value=15.0,
            z_score=3.5,
            status="NORMAL"
        ),
        "h2s_2": Node(
            id="h2s_2",
            name="H2S Sensor 2",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 20, "y": 10, "sensor_type": "H2S_TOXIC", "reading": 12.0},
            current_value=12.0,
            z_score=2.8,
            status="NORMAL"
        ),
        "lel_1": Node(
            id="lel_1",
            name="LEL Sensor 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 15, "y": 15, "sensor_type": "LEL", "reading": 5.0},
            current_value=5.0,
            z_score=0.5,
            status="NORMAL"
        ),
    }
    
    permits = {
        "permit_1": Node(
            id="permit_1",
            name="Hot Work Permit 1",
            category=NodeCategory.PERMIT,
            zone_id="zone_1",
            attributes={"x": 15, "y": 12, "permit_type": "HOT_WORK", "status": "ACTIVE"},
            status="ACTIVE"
        )
    }
    
    zones = {
        "zone_1": Node(
            id="zone_1",
            name="Zone 1",
            category=NodeCategory.ZONE,
            zone_id="zone_1",
            attributes={"x": 15, "y": 15, "radius": 20, "occupancy_level": 10},
            status="NORMAL"
        )
    }
    
    # Combine all nodes
    nodes = {}
    nodes.update(sensors)
    nodes.update(permits)
    nodes.update(zones)
    
    # Create graph engine
    graph = GraphEngine(restart_probability=0.15)
    
    # Add nodes to graph
    for node in nodes.values():
        graph.add_node(node)
    
    # Get current anomalies
    current_anomalies = {sid: s.anomaly_z_score for sid, s in sensors.items()}
    
    # Run propagation from anomalous sensors
    seed_nodes = ["h2s_1", "h2s_2"]
    pagerank_scores, contributing_weights = graph.compute_risk_score(
        seed_nodes=seed_nodes,
        current_anomalies=current_anomalies
    )
    
    print(f"\nPropagation from seed nodes: {seed_nodes}")
    print("\nPageRank scores:")
    for node_id, score in sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True):
        print(f"  {node_id}: {score:.4f}")
    
    print(f"\nContributing weights for top node:")
    top_node = max(pagerank_scores.items(), key=lambda x: x[1])[0]
    for contrib_id, weight in contributing_weights[top_node][:5]:
        print(f"  {contrib_id}: {weight:.4f}")
    
    print()


def example_rule_guard():
    """Demonstrate rule-guard layer with statutory checks."""
    print("=" * 60)
    print("Example: Rule-Guard Layer with Statutory Checks")
    print("=" * 60)
    
    # Create test scenario that triggers rule-guard
    now = datetime.now()
    
    sensors = {
        "h2s_sensor_1": SensorNode(
            node_id="h2s_sensor_1",
            location=(15, 12, 0),
            hazard_type=HazardType.H2S,
            current_value=15.0,  # > 10ppm threshold
            anomaly_z_score=3.5,
            hazard_severity=2.5
        )
    }
    
    permits = {
        "permit_1": PermitNode(
            node_id="permit_1",
            location=(15, 12, 0),
            permit_type=PermitType.HOT_WORK,
            is_active=True,
            valid_from=now - timedelta(hours=1),
            valid_until=now + timedelta(hours=8),
            hazard_severity=1.5
        )
    }
    
    zones = {
        "zone_1": ZoneNode(
            node_id="zone_1",
            location=(15, 15, 0),
            radius=20,
            occupancy_level=5,
            hazard_severity=1.0
        )
    }
    
    # Create rule-guard
    rule_guard = RuleGuard()
    
    # Evaluate rules
    triggered_rules = rule_guard.evaluate_rules(sensors, permits, zones)
    
    print(f"\nTriggered rules: {len(triggered_rules)}")
    for rule_desc, alert_level, contributing_nodes in triggered_rules:
        print(f"\n  Rule: {rule_desc}")
        print(f"  Alert Level: {alert_level.value}")
        print(f"  Contributing Nodes: {contributing_nodes}")
    
    print()


def example_full_alert_system():
    """Demonstrate the complete alert system with both layers."""
    print("=" * 60)
    print("Example: Complete Alert System (Propagation + Rule-Guard)")
    print("=" * 60)
    
    # Create alert system
    alert_system = AlertSystem(restart_probability=0.15)
    
    # Create test scenario with correlated anomalies
    now = datetime.now()
    
    sensors = {
        "h2s_sensor_1": Node(
            id="h2s_sensor_1",
            name="H2S Sensor 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 10, "y": 10, "sensor_type": "H2S_TOXIC", "reading": 15.0},
            current_value=15.0,
            z_score=3.5,
            status="NORMAL"
        ),
        "h2s_sensor_2": Node(
            id="h2s_sensor_2",
            name="H2S Sensor 2",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 20, "y": 10, "sensor_type": "H2S_TOXIC", "reading": 12.0},
            current_value=12.0,
            z_score=2.8,
            status="NORMAL"
        ),
        "lel_sensor_1": Node(
            id="lel_sensor_1",
            name="LEL Sensor 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 15, "y": 15, "sensor_type": "LEL", "reading": 5.0},
            current_value=5.0,
            z_score=0.5,
            status="NORMAL"
        ),
    }
    
    permits = {
        "permit_1": Node(
            id="permit_1",
            name="Hot Work Permit 1",
            category=NodeCategory.PERMIT,
            zone_id="zone_1",
            attributes={
                "x": 15,
                "y": 12,
                "permit_type": "HOT_WORK",
                "status": "INACTIVE",  # Deactivated to avoid rule-guard trigger
                "start_time": (now - timedelta(hours=1)).isoformat(),
                "end_time": (now + timedelta(hours=8)).isoformat()
            },
            status="INACTIVE"
        )
    }
    
    zones = {
        "zone_1": Node(
            id="zone_1",
            name="Zone 1",
            category=NodeCategory.ZONE,
            zone_id="zone_1",
            attributes={"x": 15, "y": 15, "radius": 20, "occupancy_level": 10},
            status="NORMAL"
        )
    }
    
    # Combine all nodes
    nodes = {}
    nodes.update(sensors)
    nodes.update(permits)
    nodes.update(zones)
    
    # Evaluate alerts
    alerts = alert_system.evaluate(nodes)
    
    print(f"\nGenerated alerts: {len(alerts)}")
    for alert in alerts:
        print(f"\n  Alert ID: {alert.alert_id}")
        print(f"  Layer: {alert.layer_source}")
        print(f"  Risk Score: {alert.risk_score:.4f}")
        print(f"  Confidence: {alert.confidence:.4f}")
        print(f"  Evidence Completeness: {alert.evidence_completeness:.4f}")
        print(f"  Alert Level: {alert.alert_level.value}")
        print(f"  Contributing Nodes: {len(alert.contributing_nodes)}")
        for node_id, weight in alert.contributing_nodes[:3]:
            print(f"    {node_id}: {weight:.4f}")
    
    # Get top alert
    top_alert = alert_system.get_top_alert(alerts)
    if top_alert:
        print(f"\n  TOP ALERT: {top_alert.alert_id}")
        print(f"  Level: {top_alert.alert_level.value}")
        print(f"  Layer: {top_alert.layer_source}")
    
    print()


def example_parameter_fitting():
    """Demonstrate parameter fitting with gradient-boosted regression."""
    print("=" * 60)
    print("Example: Parameter Fitting with Gradient-Boosted Regression")
    print("=" * 60)
    
    # Load training data from scenarios.json (generated by Antigravity's service)
    fitter = ParameterFitter(model_dir="models")
    
    try:
        print("\nLoading training dataset from scenarios.json...")
        samples = fitter.load_scenarios_from_json("scenarios.json")
        print(f"Loaded {len(samples)} training samples")
        
        # Train parameter fitter
        print("\nTraining gradient-boosted regression models...")
        metrics = fitter.train(samples, test_size=0.2)
        
        print("\nTraining metrics:")
        print(f"  Severity MSE: {metrics['severity_mse']:.4f}")
        print(f"  Severity R²: {metrics['severity_r2']:.4f}")
        print(f"  Decay MSE: {metrics['decay_mse']:.4f}")
        print(f"  Decay R²: {metrics['decay_r2']:.4f}")
        
        # Get feature importance
        sev_imp, dec_imp = fitter.get_feature_importance()
        print("\nTop 5 features for severity prediction:")
        for feat, imp in sorted(sev_imp.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {feat}: {imp:.4f}")
        
        # Predict on a sample
        test_sample = samples[0]
        severity, decay = fitter.predict(test_sample)
        print(f"\nPrediction for sample {test_sample.sensor_id}:")
        print(f"  Predicted severity: {severity:.4f} (true: {test_sample.true_severity:.4f})")
        print(f"  Predicted decay: {decay:.4f} (true: {test_sample.true_decay:.4f})")
        
        # Save models
        fitter.save_models()
        print("\nModels saved to 'models/' directory")
        
    except FileNotFoundError:
        print("\nscenarios.json not found.")
        print("This file should be generated by Antigravity's scenario_generator service.")
        print("Please ensure scenarios.json is available before running this example.")
    
    print()


def example_single_anomaly_test():
    """Demonstrate that single anomaly doesn't trigger COMPOUND_CRITICAL."""
    print("=" * 60)
    print("Example: Single Anomaly Test (Should NOT trigger COMPOUND_CRITICAL)")
    print("=" * 60)
    
    alert_system = AlertSystem()
    now = datetime.now()
    
    # Create single anomaly scenario
    sensors = {
        "h2s_sensor_1": Node(
            id="h2s_sensor_1",
            name="H2S Sensor 1",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 10, "y": 10, "sensor_type": "H2S_TOXIC", "reading": 15.0},
            current_value=15.0,
            z_score=3.5,
            status="NORMAL"
        ),
        "h2s_sensor_2": Node(
            id="h2s_sensor_2",
            name="H2S Sensor 2",
            category=NodeCategory.SENSOR,
            zone_id="zone_1",
            attributes={"x": 20, "y": 10, "sensor_type": "H2S_TOXIC", "reading": 2.0},
            current_value=2.0,
            z_score=0.5,
            status="NORMAL"
        ),
    }
    
    permits = {
        "permit_1": Node(
            id="permit_1",
            name="Hot Work Permit 1",
            category=NodeCategory.PERMIT,
            zone_id="zone_1",
            attributes={
                "x": 15,
                "y": 12,
                "permit_type": "HOT_WORK",
                "status": "INACTIVE",  # Deactivated to avoid rule-guard trigger
                "start_time": (now - timedelta(hours=1)).isoformat(),
                "end_time": (now + timedelta(hours=8)).isoformat()
            },
            status="INACTIVE"
        )
    }
    
    zones = {
        "zone_1": Node(
            id="zone_1",
            name="Zone 1",
            category=NodeCategory.ZONE,
            zone_id="zone_1",
            attributes={"x": 15, "y": 15, "radius": 20, "occupancy_level": 10},
            status="NORMAL"
        )
    }
    
    nodes = {}
    nodes.update(sensors)
    nodes.update(permits)
    nodes.update(zones)
    
    alerts = alert_system.evaluate(nodes)
    
    print(f"\nGenerated alerts: {len(alerts)}")
    compound_critical = [a for a in alerts if a.alert_level == AlertLevel.COMPOUND_CRITICAL]
    
    print(f"COMPOUND_CRITICAL alerts: {len(compound_critical)}")
    if len(compound_critical) == 0:
        print("✓ Test passed: Single anomaly did not trigger COMPOUND_CRITICAL")
    else:
        print("✗ Test failed: Single anomaly triggered COMPOUND_CRITICAL")
    
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("SPATIO-TEMPORAL WEIGHTED PROPAGATION GRAPH ENGINE")
    print("Example Usage Demonstration")
    print("=" * 60 + "\n")
    
    # Run examples
    example_time_bucketing()
    example_graph_propagation()
    example_rule_guard()
    example_full_alert_system()
    example_parameter_fitting()
    example_single_anomaly_test()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

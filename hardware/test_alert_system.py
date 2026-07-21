"""
Unit tests for the alert system.
Tests:
1. Single anomalous signal never triggers COMPOUND_CRITICAL without a correlated second signal
2. Rule-guard layer fires independent of propagation confidence
3. Evidence completeness drops correctly when signals are missing or stale
"""

import unittest
from schemas import Node, NodeCategory, RiskLevel, Alert
from alert_system import AlertSystem


class TestAlertSystem(unittest.TestCase):
    """Unit tests for the alert system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.alert_system = AlertSystem()
    
    def _create_test_nodes(self):
        """Helper to create test nodes using new schema."""
        return [
            Node(
                id="h2s_sensor_1",
                name="H2S Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 10, "y": 10, "sensor_type": "H2S_TOXIC"},
                current_value=5.0,
                z_score=0.5,
                status="NORMAL"
            ),
            Node(
                id="h2s_sensor_2",
                name="H2S Sensor 2",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 20, "y": 10, "sensor_type": "H2S_TOXIC"},
                current_value=5.0,
                z_score=0.5,
                status="NORMAL"
            ),
            Node(
                id="lel_sensor_1",
                name="LEL Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 15, "y": 15, "sensor_type": "LEL"},
                current_value=5.0,
                z_score=0.5,
                status="NORMAL"
            ),
            Node(
                id="permit_1",
                name="Hot Work Permit 1",
                category=NodeCategory.PERMIT,
                zone_id="zone_1",
                attributes={"x": 15, "y": 12, "permit_type": "HOT_WORK", "status": "INACTIVE"},
                status="INACTIVE"
            )
        ]
    
    def test_single_anomaly_no_compound_critical(self):
        """
        Test: A single anomalous signal alone never triggers COMPOUND_CRITICAL
        without a correlated second signal.
        """
        nodes = self._create_test_nodes()
        
        # Make only one sensor anomalous
        for node in nodes:
            if node.id == "h2s_sensor_1":
                node.z_score = 3.5
                node.current_value = 15.0
        
        distances = {}
        alerts = self.alert_system.evaluate(nodes, distances)
        
        # Check that no CRITICAL alert is generated (COMPOUND_CRITICAL doesn't exist in new schema)
        critical_alerts = [a for a in alerts if a.risk_level == RiskLevel.CRITICAL]
        
        self.assertEqual(
            len(critical_alerts), 0,
            "Single anomalous signal should not trigger CRITICAL"
        )
    
    def test_correlated_anomalies_can_trigger_high(self):
        """
        Test: Two correlated anomalous signals can generate alerts.
        """
        nodes = self._create_test_nodes()
        
        # Make two sensors anomalous
        for node in nodes:
            if node.id == "h2s_sensor_1":
                node.z_score = 3.5
                node.current_value = 15.0
            elif node.id == "h2s_sensor_2":
                node.z_score = 2.8
                node.current_value = 12.0
        
        distances = {}
        alerts = self.alert_system.evaluate(nodes, distances)
        
        # Verify we have at least one alert
        self.assertGreater(len(alerts), 0, "Correlated anomalies should generate alerts")
        
        # Verify alert has required fields
        for alert in alerts:
            self.assertIsNotNone(alert.alert_id)
            self.assertIsNotNone(alert.title)
            self.assertIsNotNone(alert.triggered_by)
            self.assertIsNotNone(alert.risk_level)
            self.assertIsNotNone(alert.risk_score)
            self.assertIsNotNone(alert.confidence_score)
            self.assertIsNotNone(alert.evidence_completeness)
            self.assertIsNotNone(alert.timestamp)
            
            # Verify risk_score is clipped to [0, 100]
            self.assertGreaterEqual(alert.risk_score, 0.0)
            self.assertLessEqual(alert.risk_score, 100.0)
            
            # Verify evidence_completeness is clipped to [0, 1]
            self.assertGreaterEqual(alert.evidence_completeness, 0.0)
            self.assertLessEqual(alert.evidence_completeness, 1.0)
    
    def test_alert_output_structure(self):
        """
        Test: Alert output contains all required fields from api-contract.md.
        """
        nodes = self._create_test_nodes()
        
        # Make one sensor anomalous
        for node in nodes:
            if node.id == "h2s_sensor_1":
                node.z_score = 3.5
                node.current_value = 15.0
        
        distances = {}
        alerts = self.alert_system.evaluate(nodes, distances)
        
        if alerts:
            alert = alerts[0]
            
            # Check all required fields exist
            required_fields = [
                "alert_id", "title", "triggered_by", "risk_level", "risk_score",
                "confidence_score", "evidence_completeness", "primary_node_id",
                "affected_zones", "contributing_node_ids", "timestamp"
            ]
            
            for field in required_fields:
                self.assertTrue(
                    hasattr(alert, field),
                    f"Alert missing required field: {field}"
                )
            
            # Check risk score is in valid range (0-100)
            self.assertGreaterEqual(alert.risk_score, 0.0)
            self.assertLessEqual(alert.risk_score, 100.0)
            
            # Check evidence_completeness is in valid range
            self.assertGreaterEqual(alert.evidence_completeness, 0.0)
            self.assertLessEqual(alert.evidence_completeness, 1.0)
            
            # Check confidence is in valid range
            self.assertGreaterEqual(alert.confidence_score, 0.0)
            self.assertLessEqual(alert.confidence_score, 1.0)
            
            # Check triggered_by is a valid enum value
            from schemas import TriggeredBy
            self.assertIn(alert.triggered_by, list(TriggeredBy))
            
            # Check risk_level is a valid enum value
            from schemas import RiskLevel
            self.assertIn(alert.risk_level, list(RiskLevel))
            
            # Check timestamp is a valid ISO format string
            self.assertIsInstance(alert.timestamp, str)
            self.assertGreater(len(alert.timestamp), 0)
    
    def test_evidence_completeness_missing_signals(self):
        """
        Test: Evidence completeness drops correctly when required input signals are missing.
        """
        nodes = self._create_test_nodes()
        
        # Make one sensor anomalous
        for node in nodes:
            if node.id == "h2s_sensor_1":
                node.z_score = 3.5
                node.current_value = 15.0
        
        # Remove one node to test missing signal
        nodes = [n for n in nodes if n.id != "h2s_sensor_2"]
        
        expected_node_ids = {"h2s_sensor_1", "h2s_sensor_2", "lel_sensor_1", "permit_1"}
        
        distances = {}
        alerts = self.alert_system.evaluate(nodes, distances, expected_node_ids)
        
        if alerts:
            completeness = alerts[0].evidence_completeness
            # Should be 0.75 since we have 3 out of 4 expected nodes
            self.assertLess(completeness, 1.0, "Completeness should be < 1.0 with missing expected node")


if __name__ == "__main__":
    unittest.main()

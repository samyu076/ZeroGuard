"""
Schema conformance tests to verify Alert objects match api-contract.md exactly.
"""

import unittest
from schemas import Alert, TriggeredBy, RiskLevel, RuleGuardResult
from alert_system import AlertSystem
from data_loader import ScenarioDataLoader


class TestSchemaConformance(unittest.TestCase):
    """Test that Alert objects conform to the frozen api-contract.md schema."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.alert_system = AlertSystem()
        self.data_loader = ScenarioDataLoader()
        
    def test_alert_has_all_required_fields(self):
        """
        Test: Alert object contains all required fields from api-contract.md.
        Required fields: alert_id, title, triggered_by, risk_level, risk_score,
        confidence_score, evidence_completeness, primary_node_id, affected_zones,
        contributing_node_ids, timestamp
        """
        # Load a scenario and create nodes
        self.data_loader.load_all()
        scenario = self.data_loader.scenarios[0]
        nodes = self.data_loader.scenario_to_nodes(scenario)
        distances = self.data_loader.get_all_sensor_permit_distances(scenario)
        
        # Evaluate to generate alerts
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
            
            # Verify field types match schema
            self.assertIsInstance(alert.alert_id, str)
            self.assertIsInstance(alert.title, str)
            self.assertIsInstance(alert.triggered_by, TriggeredBy)
            self.assertIsInstance(alert.risk_level, RiskLevel)
            self.assertIsInstance(alert.risk_score, float)
            self.assertIsInstance(alert.confidence_score, float)
            self.assertIsInstance(alert.evidence_completeness, float)
            self.assertIsInstance(alert.primary_node_id, str)
            self.assertIsInstance(alert.affected_zones, list)
            self.assertIsInstance(alert.contributing_node_ids, dict)
            self.assertIsInstance(alert.timestamp, str)
            
            # Verify value ranges
            self.assertGreaterEqual(alert.risk_score, 0.0)
            self.assertLessEqual(alert.risk_score, 100.0)
            self.assertGreaterEqual(alert.confidence_score, 0.0)
            self.assertLessEqual(alert.confidence_score, 1.0)
            self.assertGreaterEqual(alert.evidence_completeness, 0.0)
            self.assertLessEqual(alert.evidence_completeness, 1.0)
    
    def test_triggered_by_enum_values(self):
        """
        Test: triggered_by field only contains valid enum values.
        Must be either "rule_guard" or "propagation".
        """
        self.data_loader.load_all()
        scenario = self.data_loader.scenarios[0]
        nodes = self.data_loader.scenario_to_nodes(scenario)
        distances = self.data_loader.get_all_sensor_permit_distances(scenario)
        
        alerts = self.alert_system.evaluate(nodes, distances)
        
        for alert in alerts:
            self.assertIn(
                alert.triggered_by,
                [TriggeredBy.RULE_GUARD, TriggeredBy.PROPAGATION],
                f"Invalid triggered_by value: {alert.triggered_by}"
            )
    
    def test_risk_level_enum_values(self):
        """
        Test: risk_level field only contains valid enum values.
        Must be one of CRITICAL, HIGH, MEDIUM, LOW, NORMAL.
        """
        self.data_loader.load_all()
        scenario = self.data_loader.scenarios[0]
        nodes = self.data_loader.scenario_to_nodes(scenario)
        distances = self.data_loader.get_all_sensor_permit_distances(scenario)
        
        alerts = self.alert_system.evaluate(nodes, distances)
        
        for alert in alerts:
            self.assertIn(
                alert.risk_level,
                [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, 
                 RiskLevel.LOW, RiskLevel.NORMAL],
                f"Invalid risk_level value: {alert.risk_level}"
            )
    
    def test_contributing_node_ids_structure(self):
        """
        Test: contributing_node_ids is a dict with node_id -> weight mapping.
        """
        self.data_loader.load_all()
        scenario = self.data_loader.scenarios[0]
        nodes = self.data_loader.scenario_to_nodes(scenario)
        distances = self.data_loader.get_all_sensor_permit_distances(scenario)
        
        alerts = self.alert_system.evaluate(nodes, distances)
        
        for alert in alerts:
            self.assertIsInstance(alert.contributing_node_ids, dict)
            for node_id, weight in alert.contributing_node_ids.items():
                self.assertIsInstance(node_id, str)
                self.assertIsInstance(weight, (int, float))
                self.assertGreaterEqual(weight, 0.0)


if __name__ == "__main__":
    unittest.main()

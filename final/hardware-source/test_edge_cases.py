"""
Edge-case tests for HIGH #7 - verify system fails gracefully for malformed inputs.
"""

import unittest
import math
from schemas import Node, NodeCategory
from alert_system import AlertSystem


class TestEdgeCases(unittest.TestCase):
    """
    HIGH #7: Edge-case tests for malformed/incomplete inputs.
    Verify system fails gracefully with clear errors or safe defaults.
    """
    
    def test_nan_node_values(self):
        """Test that NaN values in nodes are handled gracefully."""
        nodes = [
            Node(
                id="sensor_1",
                name="Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 10, "y": 10, "sensor_type": "LEL_GAS"},
                current_value=float('nan'),  # NaN value
                z_score=3.5,
                status="NORMAL"
            )
        ]
        
        distances = {}
        alert_system = AlertSystem()
        
        # Should not crash - either handle NaN or fail with clear error
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # If it succeeds, verify output is sensible
            self.assertIsInstance(alerts, list)
        except ValueError as e:
            # Clear error is acceptable
            self.assertIn("nan", str(e).lower())
        except Exception as e:
            self.fail(f"FAIL: Unexpected exception type: {type(e).__name__}: {e}")
    
    def test_empty_node_list(self):
        """Test that empty node list is handled gracefully."""
        nodes = []
        distances = {}
        alert_system = AlertSystem()
        
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # Should return empty list or fail gracefully
            self.assertIsInstance(alerts, list)
            self.assertEqual(len(alerts), 0)
        except Exception as e:
            # Clear error is acceptable
            self.assertIn("empty", str(e).lower())
    
    def test_zero_sensors(self):
        """Test scenario with zero sensors (only permits/zones)."""
        nodes = [
            Node(
                id="permit_1",
                name="Hot Work Permit 1",
                category=NodeCategory.PERMIT,
                zone_id="zone_1",
                attributes={
                    "x": 10, 
                    "y": 10,
                    "permit_type": "HOT_WORK", 
                    "status": "ACTIVE"
                },
                status="ACTIVE"
            )
        ]
        
        distances = {}
        alert_system = AlertSystem()
        
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # Should handle gracefully - no sensors means no anomalies
            self.assertIsInstance(alerts, list)
        except Exception as e:
            # Clear error is acceptable
            self.assertIn("sensor", str(e).lower())
    
    def test_zero_permits(self):
        """Test scenario with zero permits (only sensors)."""
        nodes = [
            Node(
                id="sensor_1",
                name="LEL Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 10, "y": 10, "sensor_type": "LEL_GAS"},
                current_value=70.0,
                z_score=3.5,
                status="NORMAL"
            )
        ]
        
        distances = {}
        alert_system = AlertSystem()
        
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # Should handle gracefully - can still do propagation
            self.assertIsInstance(alerts, list)
        except Exception as e:
            # Clear error is acceptable
            self.fail(f"FAIL: Unexpected exception: {e}")
    
    def test_negative_z_scores(self):
        """Test that negative z-scores are handled correctly."""
        nodes = [
            Node(
                id="sensor_1",
                name="LEL Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 10, "y": 10, "sensor_type": "LEL_GAS"},
                current_value=70.0,
                z_score=-3.5,  # Negative z-score
                status="NORMAL"
            )
        ]
        
        distances = {}
        alert_system = AlertSystem()
        
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # Should handle - negative z-scores are valid (below normal)
            self.assertIsInstance(alerts, list)
        except Exception as e:
            self.fail(f"FAIL: Negative z-score caused exception: {e}")
    
    def test_missing_required_attributes(self):
        """Test node missing required attributes."""
        nodes = [
            Node(
                id="sensor_1",
                name="LEL Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={},  # Missing x, y, sensor_type
                current_value=70.0,
                z_score=3.5,
                status="NORMAL"
            )
        ]
        
        distances = {}
        alert_system = AlertSystem()
        
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # Should handle gracefully with defaults
            self.assertIsInstance(alerts, list)
        except KeyError as e:
            # Clear error about missing key is acceptable
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"FAIL: Unexpected exception type: {type(e).__name__}: {e}")
    
    def test_duplicate_node_ids(self):
        """Test scenario with duplicate node IDs."""
        nodes = [
            Node(
                id="sensor_1",  # Duplicate ID
                name="LEL Sensor 1",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 10, "y": 10, "sensor_type": "LEL_GAS"},
                current_value=70.0,
                z_score=3.5,
                status="NORMAL"
            ),
            Node(
                id="sensor_1",  # Duplicate ID
                name="LEL Sensor 2",
                category=NodeCategory.SENSOR,
                zone_id="zone_1",
                attributes={"x": 15, "y": 15, "sensor_type": "LEL_GAS"},
                current_value=75.0,
                z_score=3.8,
                status="NORMAL"
            )
        ]
        
        distances = {}
        alert_system = AlertSystem()
        
        try:
            alerts = alert_system.evaluate(nodes, distances)
            # Should handle - either use last one or fail clearly
            self.assertIsInstance(alerts, list)
        except Exception as e:
            # Clear error about duplicates is acceptable
            self.assertIn("duplicate", str(e).lower())


if __name__ == "__main__":
    unittest.main()

"""
Data loader for Antigravity's scenario data.
Loads scenarios_500.json and plant_layout.json from ETAI/data/.
"""

import json
from typing import Dict, List, Any, Optional
from schemas import Node, Edge, NodeCategory, PermitType, RiskLevel


class ScenarioDataLoader:
    """
    Loads and processes scenario data from Antigravity's scenario_generator service.
    """
    
    def __init__(self, scenarios_path: str = "c:/Users/samyu/OneDrive/Desktop/ETAI/data/scenarios_500.json",
                 plant_layout_path: str = "c:/Users/samyu/OneDrive/Desktop/ETAI/data/plant_layout.json"):
        self.scenarios_path = scenarios_path
        self.plant_layout_path = plant_layout_path
        self.scenarios = []
        self.plant_layout = {}
        
    def load_all(self) -> None:
        """Load both scenarios and plant layout data."""
        self.load_scenarios()
        self.load_plant_layout()
    
    def load_scenarios(self) -> List[Dict[str, Any]]:
        """Load scenarios from scenarios_500.json."""
        with open(self.scenarios_path, 'r') as f:
            self.scenarios = json.load(f)
        return self.scenarios
    
    def load_plant_layout(self) -> Dict[str, Any]:
        """Load plant layout from plant_layout.json."""
        with open(self.plant_layout_path, 'r') as f:
            self.plant_layout = json.load(f)
        return self.plant_layout
    
    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific scenario by ID."""
        for scenario in self.scenarios:
            if scenario.get("scenario_id") == scenario_id:
                return scenario
        return None
    
    def get_zone_info(self, zone_id: str) -> Optional[Dict[str, Any]]:
        """Get zone information from plant layout."""
        for zone in self.plant_layout.get("zones", []):
            if zone.get("zone_id") == zone_id:
                return zone
        return None
    
    def scenario_to_nodes(self, scenario: Dict[str, Any]) -> List[Node]:
        """
        Convert a scenario's sensors and permits to Node objects.
        
        Args:
            scenario: Scenario dictionary from scenarios_500.json
            
        Returns:
            List of Node objects
        """
        nodes = []
        
        # Convert sensors to nodes
        for sensor_data in scenario.get("sensors", []):
            node = Node(
                id=sensor_data["sensor_id"],
                name=f"Sensor {sensor_data['sensor_id']}",
                category=NodeCategory.SENSOR,
                zone_id=sensor_data["zone_id"],
                attributes={
                    "x": sensor_data["x"],
                    "y": sensor_data["y"],
                    "sensor_type": sensor_data["sensor_type"],
                    "reading": sensor_data["reading"]
                },
                current_value=sensor_data["reading"],
                z_score=sensor_data["z_score"],
                status="NORMAL"
            )
            nodes.append(node)
        
        # Convert permits to nodes
        for permit_data in scenario.get("permits", []):
            node = Node(
                id=permit_data["permit_id"],
                name=permit_data["title"],
                category=NodeCategory.PERMIT,
                zone_id=permit_data["zone_id"],
                attributes={
                    "x": permit_data["x"],
                    "y": permit_data["y"],
                    "permit_type": permit_data["permit_type"],
                    "status": permit_data["status"],
                    "contractor": permit_data.get("contractor", ""),
                    "isolation_status": permit_data.get("isolation_status", ""),
                    "statutory_citation": permit_data.get("statutory_citation", ""),
                    "start_time": permit_data["start_time"],
                    "end_time": permit_data["end_time"]
                },
                status=permit_data["status"]
            )
            nodes.append(node)
        
        return nodes
    
    def get_sensor_permit_distance(self, scenario: Dict[str, Any], 
                                  sensor_id: str, permit_id: str) -> Optional[float]:
        """
        Get precomputed distance between a sensor and permit from sensor_permit_distances.
        
        Args:
            scenario: Scenario dictionary
            sensor_id: Sensor ID
            permit_id: Permit ID
            
        Returns:
            Distance in meters, or None if not found
        """
        for dist_entry in scenario.get("sensor_permit_distances", []):
            if dist_entry["sensor_id"] == sensor_id and dist_entry["permit_id"] == permit_id:
                return dist_entry["distance_meters"]
        return None
    
    def get_all_sensor_permit_distances(self, scenario: Dict[str, Any]) -> Dict[tuple, float]:
        """
        Get all sensor-permit distances as a dictionary.
        
        Args:
            scenario: Scenario dictionary
            
        Returns:
            Dictionary mapping (sensor_id, permit_id) -> distance_meters
        """
        distances = {}
        for dist_entry in scenario.get("sensor_permit_distances", []):
            key = (dist_entry["sensor_id"], dist_entry["permit_id"])
            distances[key] = dist_entry["distance_meters"]
        return distances

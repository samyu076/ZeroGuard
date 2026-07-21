"""
ZeroGuard Scenario Data Loader
Loads scenarios_500.json and plant_layout.json using clean relative path resolution.
Converts raw JSON scenario records into graph Node and Edge models.
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from app.engine.schema import Node, Edge, NodeCategory, PermitType, RiskLevel


class ScenarioDataLoader:
    def __init__(
        self,
        data_dir: Optional[str] = None
    ):
        if not data_dir:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.data_dir = os.path.join(BASE_DIR, "data")
        else:
            self.data_dir = data_dir

        self.scenarios_path = os.path.join(self.data_dir, "scenarios_500.json")
        self.plant_layout_path = os.path.join(self.data_dir, "plant_layout.json")
        self.scenarios: List[Dict[str, Any]] = []
        self.plant_layout: Dict[str, Any] = {}

    def load_all(self) -> None:
        self.load_scenarios()
        self.load_plant_layout()

    def load_scenarios(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.scenarios_path):
            with open(self.scenarios_path, 'r', encoding='utf-8') as f:
                self.scenarios = json.load(f)
        return self.scenarios

    def load_plant_layout(self) -> Dict[str, Any]:
        if os.path.exists(self.plant_layout_path):
            with open(self.plant_layout_path, 'r', encoding='utf-8') as f:
                self.plant_layout = json.load(f)
        return self.plant_layout

    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        for scenario in self.scenarios:
            if scenario.get("scenario_id") == scenario_id:
                return scenario
        return None

    def scenario_to_nodes(self, scenario: Dict[str, Any]) -> List[Node]:
        nodes = []

        # Convert sensors to Node objects
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
                    "reading": sensor_data["reading"],
                    "hazard_severity": 1.0
                },
                current_value=sensor_data["reading"],
                z_score=sensor_data["z_score"],
                status="NORMAL" if abs(sensor_data.get("z_score", 0)) < 2.0 else "WARNING"
            )
            nodes.append(node)

        # Convert permits to Node objects
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
                    "type": permit_data["permit_type"],
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

        # Add Zone nodes from plant layout or scenario zone_id
        scenario_zone = scenario.get("zone_id", "Zone-A")
        zone_node = Node(
            id=scenario_zone,
            name=f"Plant {scenario_zone}",
            category=NodeCategory.ZONE,
            zone_id=scenario_zone,
            attributes={"center_x": 100.0, "center_y": 100.0},
            status="NORMAL"
        )
        nodes.append(zone_node)

        return nodes

    def scenario_to_edges(self, scenario: Dict[str, Any], nodes: List[Node]) -> List[Edge]:
        edges = []
        scenario_zone = scenario.get("zone_id", "Zone-A")
        for node in nodes:
            if node.category != NodeCategory.ZONE:
                edges.append(Edge(
                    source=node.id,
                    target=node.zone_id or scenario_zone,
                    relation="LOCATED_IN" if node.category == NodeCategory.PERMIT else "MONITORS",
                    weight=0.9
                ))
        return edges

    def get_all_sensor_permit_distances(self, scenario: Dict[str, Any]) -> Dict[Tuple[str, str], float]:
        distances = {}
        for dist_entry in scenario.get("sensor_permit_distances", []):
            key = (dist_entry["sensor_id"], dist_entry["permit_id"])
            distances[key] = float(dist_entry["distance_meters"])
        return distances

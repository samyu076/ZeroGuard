"""
ZeroGuard Real Graph Engine Adapter
Connects AlertSystem (PageRank propagation + RuleGuard) to ETAI FastAPI REST endpoints.
Maintains live shared in-memory scenario state and processes anomaly injection & resimulations dynamically.
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from app.engine.schema import (
    RiskGraph, Node, Edge, Alert, EvidencePath, GraphPath,
    NodeCategory, RiskLevel, TriggeredBy, AnomalyInjectionRequest, SimulationRequest
)
from app.engine.alert_system import AlertSystem
from app.engine.data_loader import ScenarioDataLoader


class RealGraphEngine:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_loader = ScenarioDataLoader(data_dir=data_dir)
        self.data_loader.load_all()
        self.alert_system = AlertSystem(restart_probability=0.15)

        # Default scenario to load: SCEN-2026-0069 (COMPOUND_CRITICAL)
        self.current_scenario_id: str = "SCEN-2026-0069"
        self._injected_anomalies: Dict[str, float] = {}
        self._offline_sensors = set()

    def load_scenario(self, scenario_id: str) -> Optional[RiskGraph]:
        scenario = self.data_loader.get_scenario_by_id(scenario_id)
        if not scenario:
            return None
        self.current_scenario_id = scenario_id
        self._injected_anomalies.clear()
        self._offline_sensors.clear()
        return self.get_current_graph_state()

    def get_current_graph_state(self) -> RiskGraph:
        scenario = self.data_loader.get_scenario_by_id(self.current_scenario_id)
        if not scenario and self.data_loader.scenarios:
            scenario = self.data_loader.scenarios[0]
            self.current_scenario_id = scenario["scenario_id"]

        if not scenario:
            # Empty fallback graph
            now_str = datetime.utcnow().isoformat() + "Z"
            return RiskGraph(
                nodes=[],
                edges=[],
                overall_risk_score=0.0,
                overall_risk_level=RiskLevel.NORMAL,
                confidence_score=1.0,
                evidence_completeness=1.0,
                active_alerts=[],
                timestamp=now_str
            )

        nodes = self.data_loader.scenario_to_nodes(scenario)
        edges = self.data_loader.scenario_to_edges(scenario, nodes)
        distances = self.data_loader.get_all_sensor_permit_distances(scenario)

        # Apply injected anomaly overrides
        for node in nodes:
            if node.id in self._injected_anomalies:
                node.z_score = self._injected_anomalies[node.id]
                if abs(node.z_score) >= 3.0:
                    node.status = "CRITICAL"
                elif abs(node.z_score) >= 2.0:
                    node.status = "WARNING"
                else:
                    node.status = "NORMAL"

        expected_node_ids = {n.id for n in nodes if n.category == NodeCategory.SENSOR}
        active_nodes = [n for n in nodes if n.id not in self._offline_sensors]

        from app.services.audit_ledger import append_to_ledger
        
        # Evaluate live alerts via AlertSystem
        alerts = self.alert_system.evaluate(nodes=active_nodes, sensor_permit_distances=distances, expected_node_ids=expected_node_ids)

        # Log new alerts
        if not hasattr(self, '_logged_alerts'):
            self._logged_alerts = set()
            
        for alert in alerts:
            if alert.alert_id not in self._logged_alerts:
                self._logged_alerts.add(alert.alert_id)
                append_to_ledger(alert.dict())

        # Compute overall risk score and level
        max_score = 0.0
        overall_level = RiskLevel.NORMAL
        for alert in alerts:
            if alert.risk_score > max_score:
                max_score = alert.risk_score
                overall_level = alert.risk_level

        if not alerts:
            # Base risk calculation from max sensor z-score
            sensor_zs = [abs(n.z_score or 0) for n in nodes if n.category == NodeCategory.SENSOR]
            max_z = max(sensor_zs) if sensor_zs else 0.0
            max_score = min(max_z * 20.0, 100.0)
            if max_z >= 3.0:
                overall_level = RiskLevel.HIGH
            elif max_z >= 2.0:
                overall_level = RiskLevel.MEDIUM
            elif max_z >= 1.5:
                overall_level = RiskLevel.LOW
            else:
                overall_level = RiskLevel.NORMAL

        now_str = datetime.utcnow().isoformat() + "Z"

        return RiskGraph(
            nodes=active_nodes,
            edges=edges,
            overall_risk_score=round(max_score, 2),
            overall_risk_level=overall_level,
            confidence_score=alerts[0].confidence_score if alerts else 0.95,
            evidence_completeness=alerts[0].evidence_completeness if alerts else 1.0,
            active_alerts=alerts,
            timestamp=now_str
        )

    def inject_sensor_anomaly(self, request: AnomalyInjectionRequest) -> RiskGraph:
        self._injected_anomalies[request.sensor_id] = request.target_z_score
        return self.get_current_graph_state()
        
    def set_sensor_status(self, sensor_id: str, offline: bool) -> RiskGraph:
        if offline:
            self._offline_sensors.add(sensor_id)
        else:
            self._offline_sensors.discard(sensor_id)
        return self.get_current_graph_state()

    def resimulate_scenario(self, request: SimulationRequest) -> RiskGraph:
        for sensor_id, z in request.injected_sensor_anomalies.items():
            self._injected_anomalies[sensor_id] = z
        return self.get_current_graph_state()

    def get_evidence_path(self, alert_id: str) -> Optional[EvidencePath]:
        current_graph = self.get_current_graph_state()

        target_alert = None
        for a in current_graph.active_alerts:
            if a.alert_id == alert_id or alert_id in a.alert_id:
                target_alert = a
                break

        if not target_alert and current_graph.active_alerts:
            target_alert = current_graph.active_alerts[0]

        if not target_alert:
            return None

        primary_node = target_alert.primary_node_id
        path_nodes = [primary_node] if primary_node else []
        for n in current_graph.nodes:
            if n.id not in path_nodes:
                path_nodes.append(n.id)

        path = GraphPath(
            path_id=f"PATH-{alert_id[:8]}",
            nodes=path_nodes[:3],
            edges=current_graph.edges[:2],
            propagation_weight=0.92,
            explanation_text=(
                f"Alert [{target_alert.title}] triggered by [{target_alert.triggered_by.value}]. "
                f"Primary node [{primary_node}] in zone(s) {target_alert.affected_zones} "
                f"evaluated with risk score {target_alert.risk_score:.1f} and confidence {target_alert.confidence_score:.2f}."
            )
        )

        sensors = [
            {"id": n.id, "name": n.name, "z_score": n.z_score, "x": n.attributes.get("x"), "y": n.attributes.get("y")}
            for n in current_graph.nodes if n.category == NodeCategory.SENSOR
        ]

        permits = [
            {"id": n.id, "type": n.attributes.get("permit_type", "PERMIT"), "zone": n.zone_id, "x": n.attributes.get("x"), "y": n.attributes.get("y")}
            for n in current_graph.nodes if n.category == NodeCategory.PERMIT
        ]

        return EvidencePath(
            alert_id=alert_id,
            triggered_by=target_alert.triggered_by,
            confidence_score=target_alert.confidence_score,
            evidence_completeness=target_alert.evidence_completeness,
            paths=[path],
            contributing_sensors=sensors,
            active_permits=permits
        )

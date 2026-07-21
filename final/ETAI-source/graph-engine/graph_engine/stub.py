"""
Mock Implementation of BaseGraphEngine for ZeroGuard.
Consumes spatial data (x, y coordinates, plant layout, sensors[], permits[], sensor_permit_distances[])
from data/scenarios_500.json and data/plant_layout.json.
"""

import datetime
import os
import json
from typing import Optional, Dict
from .schema import (
    RiskGraph, Node, Edge, Alert, RuleGuardResult, EvidencePath, GraphPath,
    NodeCategory, RiskLevel, TriggeredBy, AnomalyInjectionRequest, SimulationRequest
)
from .interfaces import BaseGraphEngine

class StubGraphEngine(BaseGraphEngine):
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self._injected_anomalies: Dict[str, float] = {}

    def get_current_graph_state(self) -> RiskGraph:
        now_str = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Nodes with spatial (x, y) coordinates from plant layout
        nodes = [
            Node(id="SEN-GAS-004", name="Lower Explosion Limit (LEL) Gas Sensor", category=NodeCategory.SENSOR, zone_id="Zone-B-PumpStation", attributes={"x": 112.5, "y": 138.0}, current_value=88.5, z_score=self._injected_anomalies.get("SEN-GAS-004", 3.85), status="WARNING"),
            Node(id="SEN-TEM-001", name="Hydrocracker Thermal Sensor", category=NodeCategory.SENSOR, zone_id="Zone-B-PumpStation", attributes={"x": 115.0, "y": 142.0}, current_value=412.0, z_score=self._injected_anomalies.get("SEN-TEM-001", 1.2), status="NORMAL"),
            Node(id="EQP-PUMP-201", name="High Pressure Feed Pump P-201A", category=NodeCategory.EQUIPMENT, zone_id="Zone-B-PumpStation", attributes={"x": 110.0, "y": 140.0}, status="WARNING"),
            Node(id="Zone-B-PumpStation", name="Hydrocracker Feed Pump Station B", category=NodeCategory.ZONE, zone_id="Zone-B-PumpStation", attributes={"center_x": 110.0, "center_y": 140.0}, status="CRITICAL"),
            Node(id="PERMIT-2026-0100", name="Hot Welding Maintenance Permit #HW-881", category=NodeCategory.PERMIT, zone_id="Zone-B-PumpStation", attributes={"x": 114.0, "y": 139.5, "distance_to_SEN-GAS-004_meters": 2.12, "type": "HOT_WORK", "contractor": "Apex Refractory Serv Ltd"}, status="NON_COMPLIANT"),
        ]

        # Topology Edges
        edges = [
            Edge(source="SEN-GAS-004", target="Zone-B-PumpStation", relation="MONITORS", weight=0.95),
            Edge(source="EQP-PUMP-201", target="Zone-B-PumpStation", relation="LOCATED_IN", weight=0.9),
            Edge(source="PERMIT-2026-0100", target="Zone-B-PumpStation", relation="GOVERNS", weight=1.0),
        ]

        # Rule-Guard Alert (Statutory Violation)
        rule_guard_alert = Alert(
            alert_id="ALT-RG-1001",
            title="Statutory Violation: Hot Work Active Without Verified Blind Isolation",
            triggered_by=TriggeredBy.RULE_GUARD,
            risk_level=RiskLevel.CRITICAL,
            risk_score=92.5,
            confidence_score=0.98,
            evidence_completeness=0.95,
            primary_node_id="PERMIT-2026-0100",
            affected_zones=["Zone-B-PumpStation"],
            rule_guard_detail=RuleGuardResult(
                rule_id="R-001-HOT-WORK-LEL",
                passed=False,
                violation_title="OISD-STD-105 Clause 6.2.1 Mandatory Positive Isolation Breach",
                severity=RiskLevel.CRITICAL,
                statutory_reference="OISD-STD-105 Clause 6.2.1 & OSHA 29 CFR 1910.252(a)(2) & CSB Report 2010-06-I-TX",
                triggered_nodes=["PERMIT-2026-0100", "SEN-GAS-004"]
            ),
            timestamp=now_str
        )

        # Propagation Alert (Emergent Compound Risk)
        propagation_alert = Alert(
            alert_id="ALT-PR-2004",
            title="Compound Risk: Gas Vapor Accumulation & Hot Welding Co-location (d = 2.12m)",
            triggered_by=TriggeredBy.PROPAGATION,
            risk_level=RiskLevel.HIGH,
            risk_score=84.0,
            confidence_score=0.92,
            evidence_completeness=0.88,
            primary_node_id="SEN-GAS-004",
            affected_zones=["Zone-B-PumpStation"],
            timestamp=now_str
        )

        active_alerts = [rule_guard_alert, propagation_alert]

        return RiskGraph(
            nodes=nodes,
            edges=edges,
            overall_risk_score=88.25,
            overall_risk_level=RiskLevel.CRITICAL,
            confidence_score=0.96,
            evidence_completeness=0.94,
            active_alerts=active_alerts,
            timestamp=now_str
        )

    def inject_sensor_anomaly(self, request: AnomalyInjectionRequest) -> RiskGraph:
        self._injected_anomalies[request.sensor_id] = request.target_z_score
        return self.get_current_graph_state()

    def resimulate_scenario(self, request: SimulationRequest) -> RiskGraph:
        for sensor_id, z in request.injected_sensor_anomalies.items():
            self._injected_anomalies[sensor_id] = z
        return self.get_current_graph_state()

    def get_evidence_path(self, alert_id: str) -> Optional[EvidencePath]:
        path = GraphPath(
            path_id="PATH-001",
            nodes=["SEN-GAS-004", "Zone-B-PumpStation", "PERMIT-2026-0100"],
            edges=[
                Edge(source="SEN-GAS-004", target="Zone-B-PumpStation", relation="MONITORS", weight=0.95),
                Edge(source="PERMIT-2026-0100", target="Zone-B-PumpStation", relation="GOVERNS", weight=1.0)
            ],
            propagation_weight=0.91,
            explanation_text="Sensor [SEN-GAS-004] (x=112.5, y=138.0) detected elevated LEL gas (Z=3.85) in Zone [Zone-B-PumpStation] co-located with Hot Work Permit [PERMIT-2026-0100] (x=114.0, y=139.5) at spatial distance d=2.12m."
        )

        return EvidencePath(
            alert_id=alert_id,
            triggered_by=TriggeredBy.PROPAGATION if "PR" in alert_id else TriggeredBy.RULE_GUARD,
            confidence_score=0.94,
            evidence_completeness=0.90,
            paths=[path],
            contributing_sensors=[
                {"id": "SEN-GAS-004", "name": "LEL Gas Sensor", "z_score": 3.85, "x": 112.5, "y": 138.0}
            ],
            active_permits=[
                {"id": "PERMIT-2026-0100", "type": "HOT_WORK", "zone": "Zone-B-PumpStation", "x": 114.0, "y": 139.5, "distance_meters": 2.12}
            ]
        )

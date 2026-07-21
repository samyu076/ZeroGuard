"""
ZeroGuard Alert System
Orchestrates GraphEngine (PageRank propagation) and RuleGuard (statutory checks).

PRECEDENCE RULE:
- Rule-guard has absolute precedence when it fires
- Propagation output is attached as supporting evidence when rule-guard fires
- When rule-guard does NOT fire, propagation determines alerts
"""

import uuid
import time
import itertools
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set

import numpy as np

from app.engine.schema import (
    Node, Alert, RiskLevel, TriggeredBy, RuleGuardResult
)
from app.engine.graph_engine import GraphEngine
from app.engine.rule_guard import RuleGuard


class AlertSystem:
    def __init__(self, restart_probability: float = 0.15):
        self.graph_engine = GraphEngine(restart_probability)
        self.rule_guard = RuleGuard()
        self.alert_counter = itertools.count()

    def _map_alert_level_to_risk_level(self, level_str: str) -> RiskLevel:
        level_str = level_str.upper()
        if "CRITICAL" in level_str:
            return RiskLevel.CRITICAL
        elif "WARNING" in level_str or "HIGH" in level_str:
            return RiskLevel.HIGH
        elif "WATCH" in level_str or "MEDIUM" in level_str:
            return RiskLevel.MEDIUM
        elif "LOW" in level_str:
            return RiskLevel.LOW
        return RiskLevel.NORMAL

    def _map_pagerank_to_risk_level(self, pagerank_score: float) -> RiskLevel:
        if pagerank_score >= 0.8:
            return RiskLevel.CRITICAL
        elif pagerank_score >= 0.6:
            return RiskLevel.HIGH
        elif pagerank_score >= 0.4:
            return RiskLevel.MEDIUM
        elif pagerank_score >= 0.2:
            return RiskLevel.LOW
        return RiskLevel.NORMAL

    def _separate_nodes_by_category(self, nodes: List[Node]) -> Dict[str, List[Node]]:
        separated = {"SENSOR": [], "PERMIT": [], "ZONE": [], "EQUIPMENT": []}
        for node in nodes:
            cat = node.category.value
            if cat in separated:
                separated[cat].append(node)
        return separated

    def _calculate_evidence_completeness(self, nodes: List[Node], expected_node_ids: Optional[Set[str]] = None) -> float:
        if expected_node_ids is None:
            return 1.0
        current_ids = {node.id for node in nodes}
        present_count = len(current_ids.intersection(expected_node_ids))
        total_expected = len(expected_node_ids)
        completeness = present_count / total_expected if total_expected > 0 else 1.0
        return max(0.0, min(completeness, 1.0))

    def evaluate(
        self,
        nodes: List[Node],
        sensor_permit_distances: Dict[tuple, float],
        expected_node_ids: Optional[Set[str]] = None
    ) -> List[Alert]:
        alerts = []
        evidence_completeness = self._calculate_evidence_completeness(nodes, expected_node_ids)

        self.graph_engine.set_nodes(nodes)
        self.graph_engine.set_sensor_permit_distances(sensor_permit_distances)

        current_anomalies = {}
        anomalous_sensors = []

        for node in nodes:
            if node.category.value == "SENSOR":
                if node.z_score is not None and np.isfinite(node.z_score):
                    current_anomalies[node.id] = node.z_score
                    if abs(node.z_score) > 2.0:
                        anomalous_sensors.append(node.id)

        # === PROPAGATION LAYER ===
        pagerank_scores = {}
        contributing_weights = {}
        propagation_confidence = 1.0
        propagation_risk_level = RiskLevel.NORMAL
        propagation_risk_score = 0.0
        propagation_primary_node = None

        if anomalous_sensors:
            pagerank_scores, contributing_weights, propagation_confidence = self.graph_engine.compute_risk_score(
                seed_nodes=anomalous_sensors,
                current_anomalies=current_anomalies
            )
            if pagerank_scores:
                max_risk = max(pagerank_scores.values())
                propagation_risk_score = max_risk * 100
                propagation_risk_level = self._map_pagerank_to_risk_level(max_risk)
                propagation_primary_node = max(pagerank_scores.items(), key=lambda x: x[1])[0]

        # === RULE-GUARD LAYER ===
        separated = self._separate_nodes_by_category(nodes)
        sensors_dict = {node.id: node for node in separated["SENSOR"]}
        permits_dict = {node.id: node for node in separated["PERMIT"]}
        zones_dict = {node.id: node for node in separated["ZONE"]}

        rule_guard_results = self.rule_guard.evaluate_rules(sensors_dict, permits_dict, zones_dict)
        rule_guard_triggered = len(rule_guard_results) > 0
        rule_guard_result = rule_guard_results[0] if rule_guard_results else None

        # === ALERT GENERATION WITH PRECEDENCE ===
        now_str = datetime.utcnow().isoformat() + "Z"

        if rule_guard_triggered and rule_guard_result:
            risk_level = self._map_alert_level_to_risk_level(rule_guard_result[1])
            risk_score = 100.0
            triggered_by = TriggeredBy.RULE_GUARD

            contributing_node_ids = {}
            if propagation_primary_node and propagation_primary_node in contributing_weights:
                contributing_node_ids = {nid: w for nid, w in contributing_weights[propagation_primary_node]}

            rg_detail = RuleGuardResult(
                rule_id="R-STATUTORY-001",
                passed=False,
                violation_title=rule_guard_result[0],
                severity=risk_level,
                statutory_reference="OISD-STD-105 Clause 6.2.1 / OSHA 29 CFR 1910.252(a)(2)",
                triggered_nodes=rule_guard_result[2]
            )

            alert = Alert(
                alert_id=str(uuid.uuid4()),
                title=f"Rule-Guard Alert: {rule_guard_result[0]}",
                triggered_by=triggered_by,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence_score=propagation_confidence,
                evidence_completeness=evidence_completeness,
                primary_node_id=rule_guard_result[2][0] if rule_guard_result[2] else (propagation_primary_node or ""),
                affected_zones=list(set(node.zone_id for node in nodes)),
                rule_guard_detail=rg_detail,
                contributing_node_ids=contributing_node_ids,
                timestamp=now_str
            )
            alerts.append(alert)

        elif propagation_risk_level != RiskLevel.NORMAL:
            affected_zones = list(set(node.zone_id for node in nodes if node.id in pagerank_scores))
            contributing_node_ids = {nid: w for nid, w in contributing_weights.get(propagation_primary_node, [])}
            risk_score = max(0.0, min(propagation_risk_score, 100.0))

            alert = Alert(
                alert_id=str(uuid.uuid4()),
                title=f"Propagation Alert: {propagation_risk_level.value} Risk Detected",
                triggered_by=TriggeredBy.PROPAGATION,
                risk_level=propagation_risk_level,
                risk_score=risk_score,
                confidence_score=propagation_confidence,
                evidence_completeness=evidence_completeness,
                primary_node_id=propagation_primary_node or "",
                affected_zones=affected_zones,
                contributing_node_ids=contributing_node_ids,
                timestamp=now_str
            )
            alerts.append(alert)

        return alerts

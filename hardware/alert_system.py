"""
Alert system combining propagation and rule-guard layers.
Outputs Alert objects matching the frozen api-contract.md schema.

PRECEDENCE RULE (from api-contract.md):
- Rule-guard has absolute precedence when it fires. If a rule-guard condition is met,
  the alert's risk_level and triggered_by = "rule_guard" are final, non-negotiable,
  regardless of propagation layer's confidence score.
- Propagation layer output is still computed and attached as supporting evidence
  (contributing_node_ids, confidence_score) when rule-guard fires.
- When rule-guard does NOT fire, triggered_by = "propagation" and graph output
  determines everything.
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from schemas import Node, Alert, TriggeredBy, RiskLevel, RuleGuardResult, NodeCategory
from graph_engine import GraphEngine
from rule_guard import RuleGuard, AlertLevel
import uuid
import numpy as np
import itertools
import time


class AlertSystem:
    """
    Main alert system combining propagation and rule-guard layers.
    Outputs Alert objects matching the frozen api-contract.md schema.
    """
    
    def __init__(self, restart_probability: float = 0.15):
        self.graph_engine = GraphEngine(restart_probability)
        self.rule_guard = RuleGuard()
        self.alert_counter = itertools.count()  # Thread-safe counter
    
    def _map_alert_level_to_risk_level(self, alert_level: AlertLevel) -> RiskLevel:
        """Map rule_guard AlertLevel enum to schemas RiskLevel enum."""
        mapping = {
            AlertLevel.NORMAL: RiskLevel.NORMAL,
            AlertLevel.LOW: RiskLevel.LOW,
            AlertLevel.MEDIUM: RiskLevel.MEDIUM,
            AlertLevel.HIGH: RiskLevel.HIGH,
            AlertLevel.CRITICAL: RiskLevel.CRITICAL,
            AlertLevel.COMPOUND_CRITICAL: RiskLevel.CRITICAL  # COMPOUND_CRITICAL maps to CRITICAL in new schema
        }
        return mapping.get(alert_level, RiskLevel.NORMAL)
    
    def _separate_nodes_by_category(self, nodes: List[Node]) -> Dict[str, List[Node]]:
        """Separate nodes by category for rule-guard processing."""
        separated = {"SENSOR": [], "PERMIT": [], "ZONE": []}
        for node in nodes:
            category = node.category.value
            if category in separated:
                separated[category].append(node)
        return separated
    
    def _map_pagerank_to_risk_level(self, pagerank_score: float) -> RiskLevel:
        """Map PageRank score (0-1) to RiskLevel enum."""
        if pagerank_score >= 0.8:
            return RiskLevel.CRITICAL
        elif pagerank_score >= 0.6:
            return RiskLevel.HIGH
        elif pagerank_score >= 0.4:
            return RiskLevel.MEDIUM
        elif pagerank_score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.NORMAL
    
    def _calculate_evidence_completeness(self,
                                       nodes: List[Node],
                                       expected_node_ids: Optional[set] = None) -> float:
        """
        Calculate evidence completeness - fraction of expected input signals that are present.
        
        Args:
            nodes: Current nodes
            expected_node_ids: Set of node IDs that should be present (if None, uses current nodes)
            
        Returns:
            Evidence completeness score (0.0 to 1.0)
        """
        if expected_node_ids is None:
            return 1.0  # No expected signals = complete
        
        current_ids = {node.id for node in nodes}
        present_count = len(current_ids.intersection(expected_node_ids))
        total_expected = len(expected_node_ids)
        
        completeness = present_count / total_expected if total_expected > 0 else 1.0
        # Clip to [0, 1] to handle edge cases
        return max(0.0, min(completeness, 1.0))
    
    def evaluate(self,
                nodes: List[Node],
                sensor_permit_distances: Dict[tuple, float],
                expected_node_ids: Optional[set] = None) -> List[Alert]:
        """
        Evaluate both propagation and rule-guard layers to generate alerts.
        
        PRECEDENCE RULE:
        - Rule-guard has absolute precedence when it fires
        - Propagation output is attached as supporting evidence when rule-guard fires
        - When rule-guard does NOT fire, propagation determines everything
        
        Args:
            nodes: List of all nodes in the graph
            sensor_permit_distances: Precomputed sensor-permit distances
            expected_node_ids: Set of node IDs that should be present for completeness check
            
        Returns:
            List of Alert objects matching api-contract.md schema
        """
        alerts = []
        
        # Calculate evidence completeness
        evidence_completeness = self._calculate_evidence_completeness(nodes, expected_node_ids)
        
        # Set up graph engine with nodes and distances
        self.graph_engine.set_nodes(nodes)
        self.graph_engine.set_sensor_permit_distances(sensor_permit_distances)
        
        # Get current anomalies from sensor nodes (with NaN validation)
        current_anomalies = {}
        anomalous_sensors = []
        invalid_sensors = []
        
        for node in nodes:
            if node.category.value == "SENSOR":
                if node.z_score is not None and np.isfinite(node.z_score):
                    current_anomalies[node.id] = node.z_score
                    if abs(node.z_score) > 2.0:
                        anomalous_sensors.append(node.id)
                else:
                    # Invalid sensor reading (NaN or infinity)
                    invalid_sensors.append(node.id)
        
        # === PROPAGATION LAYER ===
        pagerank_scores = {}
        contributing_weights = {}
        propagation_confidence = 0.0
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
        # Separate nodes by category for rule-guard
        separated = self._separate_nodes_by_category(nodes)
        sensors_dict = {node.id: node for node in separated["SENSOR"]}
        permits_dict = {node.id: node for node in separated["PERMIT"]}
        zones_dict = {node.id: node for node in separated["ZONE"]}
        
        # Evaluate rule-guard rules
        rule_guard_results = self.rule_guard.evaluate_rules(sensors_dict, permits_dict, zones_dict)
        rule_guard_triggered = len(rule_guard_results) > 0
        rule_guard_result = rule_guard_results[0] if rule_guard_results else None
        
        # === ALERT GENERATION WITH PRECEDENCE ===
        if rule_guard_triggered:
            # Rule-guard has absolute precedence
            # Use rule-guard's risk_level, but attach propagation evidence
            risk_level = self._map_alert_level_to_risk_level(rule_guard_result[1])
            risk_score = 100.0  # Rule-guard violations are max severity
            triggered_by = TriggeredBy.RULE_GUARD
            
            # Attach propagation evidence if available
            contributing_node_ids = contributing_weights.get(propagation_primary_node, {}) if propagation_primary_node else {}
            confidence_score = propagation_confidence  # Use propagation confidence as supporting evidence
            
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                title=f"Rule-Guard Alert: {rule_guard_result[0]}",
                triggered_by=triggered_by,
                risk_level=risk_level,
                risk_score=risk_score,
                confidence_score=confidence_score,
                evidence_completeness=evidence_completeness,
                primary_node_id=rule_guard_result[2][0] if rule_guard_result[2] else propagation_primary_node or "",
                affected_zones=list(set(node.zone_id for node in nodes)),
                contributing_node_ids=contributing_node_ids,
                timestamp=datetime.now().isoformat()
            )
            # Add monotonic timestamp for ordering
            alert._monotonic_timestamp = time.monotonic()
            alerts.append(alert)
        
        elif propagation_risk_level != RiskLevel.NORMAL:
            # Only propagation fired
            affected_zones = list(set(node.zone_id for node in nodes if node.id in pagerank_scores))
            contributing_node_ids = {nid: weight for nid, weight in contributing_weights.get(propagation_primary_node, [])}
            
            # Clip risk_score to [0, 100]
            risk_score = max(0.0, min(propagation_risk_score, 100.0))
            
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                title=f"Propagation Alert: {propagation_risk_level.value} Risk Detected",
                triggered_by=TriggeredBy.PROPAGATION,
                risk_level=propagation_risk_level,
                risk_score=risk_score,
                confidence_score=propagation_confidence,
                evidence_completeness=evidence_completeness,
                primary_node_id=propagation_primary_node,
                affected_zones=affected_zones,
                contributing_node_ids=contributing_node_ids,
                timestamp=datetime.now().isoformat()
            )
            # Add monotonic timestamp for ordering
            alert._monotonic_timestamp = time.monotonic()
            alerts.append(alert)
        
        return alerts

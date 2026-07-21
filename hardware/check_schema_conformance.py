"""
Verify schema conformance with api-contract.md.
"""

from schemas import Node, Edge, RiskGraph, GraphPath, RuleGuardResult, Alert, TriggeredBy, RiskLevel
import inspect

print("=" * 70)
print("SCHEMA CONFORMANCE CHECK")
print("=" * 70)

# Check Node
print("\nNode fields:")
node_fields = list(Node.__annotations__.keys())
print(f"  Actual: {node_fields}")
expected_node = ["id", "name", "category", "zone_id", "attributes", "current_value", "z_score", "status"]
print(f"  Expected: {expected_node}")
node_match = set(node_fields) == set(expected_node)
print(f"  Match: {'PASS' if node_match else 'FAIL'}")

# Check Edge
print("\nEdge fields:")
edge_fields = list(Edge.__annotations__.keys())
print(f"  Actual: {edge_fields}")
expected_edge = ["source", "target", "relation", "weight"]
print(f"  Expected: {expected_edge}")
edge_match = set(edge_fields) == set(expected_edge)
print(f"  Match: {'PASS' if edge_match else 'FAIL'}")

# Check RuleGuardResult
print("\nRuleGuardResult fields:")
rg_fields = list(RuleGuardResult.__annotations__.keys())
print(f"  Actual: {rg_fields}")
expected_rg = ["rule_id", "passed", "statutory_reference", "violation_title", "severity", "triggered_nodes"]
print(f"  Expected: {expected_rg}")
rg_match = set(rg_fields) == set(expected_rg)
print(f"  Match: {'PASS' if rg_match else 'FAIL'}")

# Check Alert
print("\nAlert fields:")
alert_fields = list(Alert.__annotations__.keys())
print(f"  Actual: {alert_fields}")
expected_alert = ["alert_id", "title", "triggered_by", "risk_level", "risk_score", 
                  "confidence_score", "evidence_completeness", "primary_node_id", 
                  "affected_zones", "rule_guard_detail", "timestamp", "contributing_node_ids"]
print(f"  Expected: {expected_alert}")
alert_match = set(alert_fields) == set(expected_alert)
print(f"  Match: {'PASS' if alert_match else 'FAIL'}")

# Check GraphPath
print("\nGraphPath fields:")
gp_fields = list(GraphPath.__annotations__.keys())
print(f"  Actual: {gp_fields}")
expected_gp = ["path_id", "nodes", "edges", "propagation_weight", "explanation_text"]
print(f"  Expected: {expected_gp}")
gp_match = set(gp_fields) == set(expected_gp)
print(f"  Match: {'PASS' if gp_match else 'FAIL'}")

# Check RiskGraph
print("\nRiskGraph fields:")
rg_fields = list(RiskGraph.__annotations__.keys())
print(f"  Actual: {rg_fields}")
expected_rg = ["nodes", "edges", "overall_risk_score", "overall_risk_level", 
               "confidence_score", "evidence_completeness", "active_alerts", "timestamp"]
print(f"  Expected: {expected_rg}")
rg_match = set(rg_fields) == set(expected_rg)
print(f"  Match: {'PASS' if rg_match else 'FAIL'}")

# Check Enums
print("\nEnum checks:")
print(f"  TriggeredBy values: {[e.value for e in TriggeredBy]}")
print(f"  Expected: ['rule_guard', 'propagation']")
print(f"  Match: {'PASS' if set([e.value for e in TriggeredBy]) == {'rule_guard', 'propagation'} else 'FAIL'}")

print(f"  RiskLevel values: {[e.value for e in RiskLevel]}")
print(f"  Expected: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NORMAL']")
print(f"  Match: {'PASS' if set([e.value for e in RiskLevel]) == {'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'NORMAL'} else 'FAIL'}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
all_pass = node_match and edge_match and rg_match and alert_match and gp_match and rg_match
print(f"Overall: {'PASS' if all_pass else 'FAIL'}")

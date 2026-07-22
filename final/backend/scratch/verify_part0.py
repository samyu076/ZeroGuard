import os, sys, json
import numpy as np

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
from app.engine.real_engine import RealGraphEngine
from app.engine.data_loader import ScenarioDataLoader
from app.engine.rule_guard import RuleGuard
from app.engine.schema import Node, NodeCategory

base_data_dir = os.path.join(os.path.dirname(backend_dir), "data")

print("=" * 60)
print("PART 0.1 - PAGERANK Z-SCORE ARITHMETIC")
print("=" * 60)

engine = RealGraphEngine(data_dir=base_data_dir)
loader = ScenarioDataLoader(data_dir=base_data_dir)
loader.load_all()

scenarios_to_check = ["SCEN-2026-0054", "SCEN-2026-0033", "SCEN-2026-0069"] # Should be SAFE, WARNING, COMPOUND_CRITICAL

distribution = {"SAFE": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0, "COMPOUND_CRITICAL": 0}
for idx, s in enumerate(loader.scenarios):
    # Just run the risk tier logic to get distribution
    engine.load_scenario(s["scenario_id"])
    graph = engine.get_current_graph_state()
    
    # Actually graph state overall_risk_score might not have tier directly mapped on graph, but we can look at alerts or label
    # Let's map risk_score to tier using engine's logic
    tier = "SAFE"
    if graph.active_alerts:
        tier = graph.active_alerts[0].risk_level.value
    elif graph.overall_risk_score >= 80: tier = "CRITICAL"
    elif graph.overall_risk_score >= 60: tier = "HIGH"
    elif graph.overall_risk_score >= 40: tier = "MEDIUM"
    elif graph.overall_risk_score >= 20: tier = "LOW"
    
    # Wait, the engine actually creates alerts. So we can just use the highest alert level.
    distribution[tier] = distribution.get(tier, 0) + 1

print(f"Full 520 Scenario Tier Distribution (Fresh Run):")
print(json.dumps(distribution, indent=2))

print("\n--- Detailed Arithmetic for 3 Scenarios ---")
for s_id in scenarios_to_check:
    engine.load_scenario(s_id)
    # The math is inside AlertSystem using GraphEngine
    graph = engine.get_current_graph_state()
    nodes = {n.id: n for n in graph.nodes}
    
    # We need to manually call compute_risk_score just like AlertSystem does
    anomalous_sensors = []
    current_anomalies = {}
    for node in graph.nodes:
        if node.category.value == "SENSOR" and node.z_score is not None:
            current_anomalies[node.id] = node.z_score
            if abs(node.z_score) > 2.0:
                anomalous_sensors.append(node.id)
                
    engine.alert_system.graph_engine.set_nodes(graph.nodes)
    raw_scores, _, _ = engine.alert_system.graph_engine.compute_risk_score(anomalous_sensors, current_anomalies)
    
    if not raw_scores:
        print(f"Scenario {s_id}: No pagerank vector.")
        continue
        
    scores_array = np.array(list(raw_scores.values()))
    mu = float(np.mean(scores_array))
    std = float(np.std(scores_array))
    
    # Pick the max scoring node
    max_node_id = max(raw_scores, key=raw_scores.get)
    max_raw = raw_scores[max_node_id]
    z_score = (max_raw - mu) / std if std > 1e-9 else 0.0
    
    # Look up risk tier based on max z-score (Graph Engine logic: z>=3.0 -> CRITICAL, etc)
    # Plus RuleGuard overrides
    actual_tier = "SAFE"
    final_risk_score = graph.overall_risk_score
    if graph.active_alerts:
        actual_tier = graph.active_alerts[0].risk_level.value
        final_risk_score = graph.active_alerts[0].risk_score
    
    print(f"\nScenario: {s_id}")
    print(f"  Target Node (Max PR): {max_node_id}")
    print(f"  Raw PageRank Score: {max_raw:.6f}")
    print(f"  Graph Mean (mu):    {mu:.6f}")
    print(f"  Graph Std Dev (std):{std:.6f}")
    print(f"  Computed Z-Score:   {z_score:.2f}")
    print(f"  Final Risk Tier:    {actual_tier} (Score: {final_risk_score:.1f})")


print("\n" + "=" * 60)
print("PART 0.2 - TTV THRESHOLDS (Thermal + Vibration)")
print("=" * 60)

def make_temp_node(val):
    return Node(id="SEN-TEM-01", name="Temp", category=NodeCategory.SENSOR, zone_id="Zone-A", attributes={"sensor_type": "TEMPERATURE"}, current_value=val, z_score=val, status="WARNING")

def make_vib_node(val):
    return Node(id="SEN-VIB-01", name="Vib", category=NodeCategory.SENSOR, zone_id="Zone-A", attributes={"sensor_type": "VIBRATION"}, current_value=val, z_score=val, status="WARNING")

rg = RuleGuard()

print("Test A: Under 10 minutes (9 mins sustained)")
import time
from unittest.mock import patch
# 0 mins
n_t1 = make_temp_node(2.5)
n_v1 = make_vib_node(2.5)
alerts = rg.evaluate_rules({"SEN-TEM-01": n_t1, "SEN-VIB-01": n_v1}, {}, {})
print(f"  At 0 mins, Alerts fired: {len(alerts)}")

# 9 mins
with patch('time.monotonic', return_value=time.monotonic() + 540):
    n_t2 = make_temp_node(2.6)
    n_v2 = make_vib_node(2.6)
    alerts = rg.evaluate_rules({"SEN-TEM-01": n_t2, "SEN-VIB-01": n_v2}, {}, {})
print(f"  At 9 mins, Alerts fired: {len(alerts)}")

# Test B: Fresh start, past 10 minutes
rg = RuleGuard()
print("\nTest B: Over 10 minutes (11 mins sustained)")
# 0 mins
n_t3 = make_temp_node(2.5)
n_v3 = make_vib_node(2.5)
alerts = rg.evaluate_rules({"SEN-TEM-01": n_t3, "SEN-VIB-01": n_v3}, {}, {})
print(f"  At 0 mins, Alerts fired: {len(alerts)}")

# 11 mins
with patch('time.monotonic', return_value=time.monotonic() + 660):
    n_t4 = make_temp_node(2.6)
    n_v4 = make_vib_node(2.6)
    alerts = rg.evaluate_rules({"SEN-TEM-01": n_t4, "SEN-VIB-01": n_v4}, {}, {})
print(f"  At 11 mins, Alerts fired: {len(alerts)}")
if alerts:
    print(f"  Alert details: {alerts[0][0]} -> {alerts[0][1]}")


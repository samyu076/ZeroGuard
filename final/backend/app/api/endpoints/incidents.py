"""
ZeroGuard Incident RCA (Root-Cause Analysis) Endpoint

GET /api/v1/incidents/{id}/explanation

Uses only data already computed by the PageRank engine (contributing_node_ids,
z_scores, permit attributes) — no new models, libraries, or external calls.
"""

from fastapi import APIRouter, HTTPException, Depends
from app.engine.real_engine import RealGraphEngine
from app.api.deps import get_graph_engine
from app.engine.schema import NodeCategory

router = APIRouter()


def _generate_rca_explanation(alert, nodes_by_id: dict) -> dict:
    """
    Generate a plain-English RCA explanation from PageRank contribution weights.

    Logic:
    - contributing_node_ids maps node_id -> contribution weight (already computed
      by GraphEngine.get_contributing_weights as edge_weight * pagerank_score)
    - Rank contributors, pick top-3
    - Build a human-readable sentence from node category + z_score/permit status
    """
    if not alert:
        return {"explanation": "No active alert found.", "contributing_factors": []}

    contributing = alert.contributing_node_ids or {}
    if not contributing:
        return {
            "explanation": (
                f"Alert '{alert.title}' was triggered by {alert.triggered_by.value}. "
                f"No PageRank propagation data available (rule-guard fired without anomalous sensor seeds)."
            ),
            "contributing_factors": []
        }

    # Sort by contribution weight descending, take top 3
    top_contributors = sorted(contributing.items(), key=lambda x: x[1], reverse=True)[:3]
    total_weight = sum(w for _, w in contributing.items())
    top_weight = sum(w for _, w in top_contributors)
    pct_explained = (top_weight / total_weight * 100) if total_weight > 1e-9 else 0.0

    factor_parts = []
    factors = []

    for rank, (node_id, weight) in enumerate(top_contributors, start=1):
        node = nodes_by_id.get(node_id)
        node_pct = (weight / total_weight * 100) if total_weight > 1e-9 else 0.0

        if node is None:
            factor_parts.append(f"node {node_id} ({node_pct:.0f}%)")
            factors.append({
                "rank": rank, "node_id": node_id, "category": "UNKNOWN",
                "contribution_pct": round(node_pct, 1), "weight": round(weight, 4),
                "detail": "Node data unavailable"
            })
            continue

        cat = node.category.value if hasattr(node.category, "value") else str(node.category)

        if cat == "SENSOR":
            z = node.z_score
            z_str = f"Z-score {z:.2f}" if z is not None else "Z-score N/A"
            sensor_type = node.attributes.get("sensor_type", "sensor").upper()
            descriptor = f"{sensor_type} sensor {node_id} ({z_str})"
            detail = f"{sensor_type} sensor recording {z_str} (anomaly threshold Z>=3.0)"
        elif cat == "PERMIT":
            p_type = node.attributes.get("permit_type", node.attributes.get("type", "PERMIT"))
            isolation = node.attributes.get("spectacle_blind_installed", None)
            iso_str = ""
            if isolation is not None:
                iso_str = " [isolation: COMPLIANT]" if isolation else " [isolation: NON-COMPLIANT — missing blind flange]"
            descriptor = f"Permit {node_id} ({p_type}{iso_str})"
            detail = f"Active {p_type} permit{iso_str} contributing {node_pct:.0f}% propagated risk"
        elif cat == "ZONE":
            descriptor = f"Zone {node.zone_id}"
            detail = f"Zone {node.zone_id} risk propagation"
        elif cat == "EQUIPMENT":
            maint = node.attributes.get("equipment_maintenance_active", False)
            descriptor = f"Equipment {node_id} ({'maintenance active' if maint else 'online'})"
            detail = f"Co-located equipment with {'active maintenance window' if maint else 'normal operation'}"
        else:
            descriptor = f"{node_id}"
            detail = f"Unknown node category"

        factor_parts.append(f"{descriptor} ({node_pct:.0f}%)")
        factors.append({
            "rank": rank,
            "node_id": node_id,
            "category": cat,
            "contribution_pct": round(node_pct, 1),
            "weight": round(weight, 4),
            "detail": detail
        })

    # Compose the summary sentence
    primary_zone = alert.affected_zones[0] if alert.affected_zones else "the affected zone"
    triggered_by_str = "statutory RuleGuard interlock" if alert.triggered_by.value == "RULE_GUARD" else "PageRank propagation engine"
    factors_str = ", and ".join(factor_parts) if len(factor_parts) <= 2 else \
                  ", ".join(factor_parts[:-1]) + f", and {factor_parts[-1]}"

    explanation = (
        f"{primary_zone}'s {alert.risk_level.value} status was triggered by the {triggered_by_str}. "
        f"It is primarily driven by {factors_str}, "
        f"which together account for {pct_explained:.0f}% of this node's propagated risk score "
        f"(alert risk score: {alert.risk_score:.1f}/100, confidence: {alert.confidence_score:.2f})."
    )

    return {
        "alert_id": alert.alert_id,
        "alert_title": alert.title,
        "risk_level": alert.risk_level.value,
        "risk_score": alert.risk_score,
        "triggered_by": alert.triggered_by.value,
        "explanation": explanation,
        "contributing_factors": factors,
        "pct_explained_by_top_factors": round(pct_explained, 1),
        "statutory_reference": (
            alert.rule_guard_detail.statutory_reference
            if alert.rule_guard_detail else "PageRank propagation — no statutory interlock"
        )
    }


@router.get("/incidents/{alert_id}/explanation")
def get_incident_explanation(
    alert_id: str,
    engine: RealGraphEngine = Depends(get_graph_engine)
):
    """
    GET /api/v1/incidents/{id}/explanation

    Auto-generate a plain-English Root-Cause Analysis (RCA) explanation for a
    CRITICAL or COMPOUND_CRITICAL alert using PageRank contribution weights already
    computed by the graph engine.

    Returns the top contributing nodes, their contribution percentage, and a
    human-readable summary sentence. Uses only data already computed — no new
    models, libraries, or external calls.
    """
    graph = engine.get_current_graph_state()
    nodes_by_id = {n.id: n for n in graph.nodes}

    # Find the alert
    target_alert = None
    for a in graph.active_alerts:
        if a.alert_id == alert_id or alert_id in a.alert_id or alert_id == "current":
            target_alert = a
            break

    # Fallback: use the most critical active alert
    if not target_alert and graph.active_alerts:
        target_alert = graph.active_alerts[0]

    if not target_alert:
        raise HTTPException(
            status_code=404,
            detail=f"No active alert found for ID '{alert_id}'. "
                   "Use 'current' to get the current alert's RCA."
        )

    return _generate_rca_explanation(target_alert, nodes_by_id)

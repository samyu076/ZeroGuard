"""
Evidence Explainer Service — Deterministic path extraction from graph state.
NO LLM narration, pure string templating from graph nodes and edges.
"""

from typing import Dict, Any, List

class EvidenceExplainerService:
    @staticmethod
    def format_evidence_path(
        alert_id: str,
        triggered_by: str,
        path_nodes: List[Dict[str, Any]],
        confidence_score: float,
        evidence_completeness: float
    ) -> Dict[str, Any]:
        """
        Constructs deterministic, zero-hallucination string templates from graph paths.
        """
        node_chain = " ──> ".join([f"{n.get('category', 'NODE')} [{n.get('id')}: {n.get('name')}]" for n in path_nodes])
        
        explanation = (
            f"[{triggered_by.upper()} ALERT {alert_id}] :: "
            f"Extracted Graph Propagation Chain: {node_chain} | "
            f"Confidence: {int(confidence_score * 100)}% | "
            f"Evidence Completeness: {int(evidence_completeness * 100)}%"
        )

        return {
            "alert_id": alert_id,
            "triggered_by": triggered_by,
            "confidence_score": confidence_score,
            "evidence_completeness": evidence_completeness,
            "explanation_text": explanation,
            "path_chain": node_chain
        }

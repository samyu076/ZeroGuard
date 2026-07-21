"""
ZeroGuard Evidence Explainer Service
Formats zero-hallucination structured evidence chains.
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
        node_str = " -> ".join([n.get("id", "NODE") for n in path_nodes])
        explanation = (
            f"Alert [{alert_id}] ({triggered_by}) confirmed via deterministic path [{node_str}] "
            f"with confidence {confidence_score * 100:.1f}% and evidence completeness {evidence_completeness * 100:.1f}%."
        )
        return {
            "alert_id": alert_id,
            "explanation_text": explanation,
            "path_chain": path_nodes,
            "confidence_score": confidence_score,
            "evidence_completeness": evidence_completeness
        }

from fastapi import APIRouter, HTTPException, Depends
from graph_engine.stub import StubGraphEngine
from graph_engine.schema import EvidencePath
from app.api.deps import get_graph_engine
from app.services.evidence_explainer import EvidenceExplainerService

router = APIRouter()

@router.get("/evidence/{alert_id}", response_model=EvidencePath)
def get_evidence(alert_id: str, engine: StubGraphEngine = Depends(get_graph_engine)):
    """
    Extract deterministic evidence path and contributing sensor/permit chain for alert.
    Executes EvidenceExplainerService to produce zero-hallucination string templates.
    """
    raw_evidence = engine.get_evidence_path(alert_id)
    if not raw_evidence:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    # Wire EvidenceExplainerService into the live execution path
    formatted = EvidenceExplainerService.format_evidence_path(
        alert_id=alert_id,
        triggered_by=raw_evidence.triggered_by.value,
        path_nodes=[{"id": n, "name": n, "category": "NODE"} for n in raw_evidence.paths[0].nodes] if raw_evidence.paths else [],
        confidence_score=raw_evidence.confidence_score,
        evidence_completeness=raw_evidence.evidence_completeness
    )

    # Attach live formatted explanation text to response path
    if raw_evidence.paths:
        raw_evidence.paths[0].explanation_text = formatted["explanation_text"]

    return raw_evidence

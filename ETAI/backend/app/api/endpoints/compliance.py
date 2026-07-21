from fastapi import APIRouter
from typing import List
from graph_engine.schema import ComplianceCheckRequest, ComplianceCitation
from app.services.compliance_citation import ComplianceCitationService
import os

router = APIRouter()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")
citation_service = ComplianceCitationService(data_dir=DATA_DIR)

@router.post("/compliance-check", response_model=List[ComplianceCitation])
def compliance_check(request: ComplianceCheckRequest):
    """
    Execute compliance retrieval against OISD / Factory Act standards.
    Evaluates real zone_id and permit parameters.
    """
    results = citation_service.search_compliance_citations(
        zone_id=request.zone_id,
        permit_type=request.permit_type.value if request.permit_type else None,
        query_text=request.query_text
    )
    return results

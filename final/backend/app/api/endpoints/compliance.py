"""
Compliance Citation Search API Endpoint
"""

from fastapi import APIRouter
from typing import List
from app.engine.schema import ComplianceCheckRequest, ComplianceCitation
from app.services.compliance_citation import ComplianceCitationService

router = APIRouter()
citation_service = ComplianceCitationService()

@router.post("/compliance-check", response_model=List[ComplianceCitation])
def compliance_check(request: ComplianceCheckRequest):
    """
    Execute statutory compliance retrieval against OISD / Factory Act standards.
    Evaluates real zone_id, permit_type, isolation_status, and gas_z_score dynamically.
    """
    results = citation_service.search_compliance_citations(
        zone_id=request.zone_id,
        permit_type=request.permit_type.value if request.permit_type else None,
        query_text=request.query_text,
        isolation_status=request.isolation_status,
        gas_z_score=request.gas_z_score
    )
    return results

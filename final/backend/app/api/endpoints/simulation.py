"""
Resimulate Scenario API Endpoint
"""

from fastapi import APIRouter, Depends
from app.engine.schema import SimulationRequest, RiskGraph
from app.engine.real_engine import RealGraphEngine
from app.api.deps import get_graph_engine

router = APIRouter()

@router.post("/resimulate", response_model=RiskGraph)
def resimulate(request: SimulationRequest, engine: RealGraphEngine = Depends(get_graph_engine)):
    """
    Re-evaluate risk propagation scenario across active permits and sensor overrides.
    """
    return engine.resimulate_scenario(request)

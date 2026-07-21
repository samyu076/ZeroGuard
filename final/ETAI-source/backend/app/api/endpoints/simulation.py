from fastapi import APIRouter, Depends
from graph_engine.stub import StubGraphEngine
from graph_engine.schema import SimulationRequest, RiskGraph
from app.api.deps import get_graph_engine

router = APIRouter()

@router.post("/resimulate", response_model=RiskGraph)
def resimulate(request: SimulationRequest, engine: StubGraphEngine = Depends(get_graph_engine)):
    """
    Re-evaluate risk propagation scenario across active permits and sensor overrides in shared memory state.
    """
    return engine.resimulate_scenario(request)

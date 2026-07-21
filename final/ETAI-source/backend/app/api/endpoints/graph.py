from fastapi import APIRouter, Depends
from graph_engine.stub import StubGraphEngine
from graph_engine.schema import RiskGraph
from app.api.deps import get_graph_engine

router = APIRouter()

@router.get("/graph-state", response_model=RiskGraph)
def get_graph_state(engine: StubGraphEngine = Depends(get_graph_engine)):
    """
    Fetch current industrial risk graph state, nodes, edges & active alerts.
    Consumes shared singleton Graph Engine state.
    """
    return engine.get_current_graph_state()

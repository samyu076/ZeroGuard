"""
Graph State API Endpoint
"""

from fastapi import APIRouter, Depends
from app.engine.schema import RiskGraph
from app.engine.real_engine import RealGraphEngine
from app.api.deps import get_graph_engine

router = APIRouter()

@router.get("/graph-state", response_model=RiskGraph)
def get_graph_state(engine: RealGraphEngine = Depends(get_graph_engine)):
    """
    Fetch current evaluated industrial risk graph state using live PageRank and RuleGuard logic.
    """
    return engine.get_current_graph_state()

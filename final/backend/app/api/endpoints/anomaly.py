"""
Anomaly Injection API Endpoint
"""

from fastapi import APIRouter, Depends
from app.engine.schema import AnomalyInjectionRequest, RiskGraph
from app.engine.real_engine import RealGraphEngine
from app.api.deps import get_graph_engine

router = APIRouter()

@router.post("/inject-anomaly", response_model=RiskGraph)
def inject_anomaly(request: AnomalyInjectionRequest, engine: RealGraphEngine = Depends(get_graph_engine)):
    """
    Inject z-score anomaly override into active graph engine state and re-evaluate risk.
    """
    return engine.inject_sensor_anomaly(request)

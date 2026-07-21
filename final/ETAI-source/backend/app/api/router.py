from fastapi import APIRouter
from app.api.endpoints import graph, anomaly, simulation, evidence, compliance, scenarios

api_router = APIRouter(prefix="/api")

api_router.include_router(graph.router, tags=["Graph State"])
api_router.include_router(anomaly.router, tags=["Anomaly Injection"])
api_router.include_router(simulation.router, tags=["Simulation"])
api_router.include_router(evidence.router, tags=["Evidence Explainer"])
api_router.include_router(compliance.router, tags=["Compliance Citation"])
api_router.include_router(scenarios.router, tags=["Scenarios & Plant Layout"])

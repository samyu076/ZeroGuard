"""
ZeroGuard API Router
Includes all REST endpoints under /api/v1 prefix.
"""

from fastapi import APIRouter
from app.api.endpoints import (
    scenarios, graph, anomaly, simulation,
    evidence, compliance, metrics, esd, scada_telemetry, incidents
)

api_router = APIRouter()
api_router.include_router(scenarios.router, tags=["scenarios"])
api_router.include_router(graph.router, tags=["graph"])
api_router.include_router(anomaly.router, tags=["anomaly"])
api_router.include_router(simulation.router, tags=["simulation"])
api_router.include_router(evidence.router, tags=["evidence"])
api_router.include_router(compliance.router, tags=["compliance"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(esd.router, tags=["esd"])
api_router.include_router(scada_telemetry.router, tags=["scada"])
api_router.include_router(incidents.router, tags=["incidents"])

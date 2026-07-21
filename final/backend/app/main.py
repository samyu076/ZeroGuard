"""
ZeroGuard FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(
    title="ZeroGuard Compound Industrial Risk Intelligence Platform",
    description="FastAPI Backend Gateway for Spatio-Temporal PageRank Risk Propagation & Statutory Rule Guard",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include unified API Router under /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "ZeroGuard Platform Gateway",
        "engine": "Live PageRank Propagation + RuleGuard"
    }

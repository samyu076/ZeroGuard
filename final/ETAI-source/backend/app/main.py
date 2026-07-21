import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Dynamically add graph-engine module to python path for monorepo development
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GRAPH_ENGINE_DIR = os.path.join(BASE_DIR, "graph-engine")
if GRAPH_ENGINE_DIR not in sys.path:
    sys.path.insert(0, GRAPH_ENGINE_DIR)

from app.api.router import api_router

app = FastAPI(
    title="ZeroGuard — Compound Industrial Risk Intelligence API",
    description="FastAPI Gateway exposing frozen contract endpoints for risk graph, anomaly injection, evidence explanation, and compliance citations.",
    version="1.0.0"
)

# Enable CORS for React Frontend Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "ZeroGuard API Gateway",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

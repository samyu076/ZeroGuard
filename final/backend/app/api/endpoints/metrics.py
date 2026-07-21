import os
import json
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/metrics")
def get_baseline_metrics():
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    base_dir = os.path.dirname(backend_dir)
    metrics_path = os.path.join(base_dir, "data", "metrics.json")
    
    if not os.path.exists(metrics_path):
        # Fallback check if path differs
        metrics_path = os.path.join(backend_dir, "data", "metrics.json")
        if not os.path.exists(metrics_path):
            raise HTTPException(status_code=404, detail=f"Metrics file not found at {metrics_path}")
        
    with open(metrics_path, "r", encoding="utf-8") as f:
        return json.load(f)

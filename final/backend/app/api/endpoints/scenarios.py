"""
Scenarios API Endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from app.services.scenario_generator import ScenarioGeneratorService
from app.engine.real_engine import RealGraphEngine
from app.api.deps import get_graph_engine

router = APIRouter()
scenario_service = ScenarioGeneratorService()

@router.get("/scenarios", response_model=List[Dict[str, Any]])
def get_scenarios(label: Optional[str] = Query(None, description="Filter by SAFE, WATCH, WARNING, COMPOUND_CRITICAL")):
    if label:
        return scenario_service.get_scenarios_by_label(label.upper())
    return scenario_service.get_all_scenarios()

@router.get("/scenarios/{scenario_id}", response_model=Dict[str, Any])
def get_scenario_by_id(scenario_id: str, engine: RealGraphEngine = Depends(get_graph_engine)):
    scen = scenario_service.get_scenario_by_id(scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    # Active engine loads the scenario state
    engine.load_scenario(scenario_id)
    return scen

@router.get("/plant-layout", response_model=Dict[str, Any])
def get_plant_layout():
    return scenario_service.get_plant_layout()


@router.get("/scenarios/{scenario_id}/replay")
def get_scenario_replay(
    scenario_id: str, 
    window_minutes: int = 30,
    engine: RealGraphEngine = Depends(get_graph_engine)
):
    """
    Forensic DVR Replay:
    Fetches the chronological sequence of scenarios leading up to a specific incident.
    This provides a strictly read-only historical rewind of the plant state for explainability.
    """
    target_scen = scenario_service.get_scenario_by_id(scenario_id)
    if not target_scen:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    try:
        from datetime import datetime, timedelta
        target_time = datetime.fromisoformat(target_scen["timestamp"].replace("Z", "+00:00"))
        start_time = target_time - timedelta(minutes=window_minutes)
        
        target_zone = target_scen.get("zone_id")
        
        all_scenarios = scenario_service.get_all_scenarios()
        
        replay_sequence = []
        for s in all_scenarios:
            s_time = datetime.fromisoformat(s["timestamp"].replace("Z", "+00:00"))
            # Only include scenarios leading up to and including the target scenario
            if start_time <= s_time <= target_time:
                # Filter by the same zone if applicable, or include all if we want plant-wide
                if target_zone and s.get("zone_id") != target_zone:
                    continue
                    
                replay_sequence.append({
                    "scenario_id": s["scenario_id"],
                    "timestamp": s["timestamp"],
                    "ground_truth_label": s.get("ground_truth_label", "SAFE"),
                    "risk_score": s.get("risk_score", 0),
                    "sensors": s.get("sensors", []),
                    "permits": s.get("permits", [])
                })
                
        # Sort chronologically just in case
        replay_sequence.sort(key=lambda x: datetime.fromisoformat(x["timestamp"].replace("Z", "+00:00")))
        
        return {
            "target_scenario_id": scenario_id,
            "target_timestamp": target_scen["timestamp"],
            "window_minutes": window_minutes,
            "replay_sequence": replay_sequence,
            "total_frames": len(replay_sequence)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating replay sequence: {str(e)}")

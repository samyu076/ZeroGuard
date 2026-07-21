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

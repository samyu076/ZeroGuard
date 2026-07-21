from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.services.scenario_generator import ScenarioGeneratorService

router = APIRouter()
scenario_service = ScenarioGeneratorService()

@router.get("/scenarios", response_model=List[Dict[str, Any]])
def get_scenarios(label: Optional[str] = Query(None, description="Filter by SAFE, WATCH, WARNING, COMPOUND_CRITICAL")):
    """
    Fetch all 520 labeled industrial scenarios from scenarios_500.json.
    """
    if label:
        return scenario_service.get_scenarios_by_label(label.upper())
    return scenario_service.get_all_scenarios()

@router.get("/scenarios/{scenario_id}", response_model=Dict[str, Any])
def get_scenario_by_id(scenario_id: str):
    """
    Fetch a specific scenario by scenario_id (e.g. SCEN-2026-0240).
    """
    scen = scenario_service.get_scenario_by_id(scenario_id)
    if not scen:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    return scen

@router.get("/plant-layout", response_model=Dict[str, Any])
def get_plant_layout():
    """
    Fetch shared 5-zone plant layout coordinates and grid metadata.
    """
    return scenario_service.get_plant_layout()

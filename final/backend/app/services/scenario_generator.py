"""
Scenario Generator Loader & Service
Loads 520 scenarios and plant layout from final/data/.
"""

import json
import os
from typing import List, Dict, Any, Optional


class ScenarioGeneratorService:
    def __init__(self, data_dir: Optional[str] = None):
        if not data_dir:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.data_dir = os.path.join(BASE_DIR, "data")
        else:
            self.data_dir = data_dir

        self._scenarios: List[Dict[str, Any]] = []
        self._plant_layout: Dict[str, Any] = {}
        self._load_data()

    def _load_data(self):
        scen_path = os.path.join(self.data_dir, "scenarios_500.json")
        if os.path.exists(scen_path):
            with open(scen_path, "r", encoding="utf-8") as f:
                self._scenarios = json.load(f)

        layout_path = os.path.join(self.data_dir, "plant_layout.json")
        if os.path.exists(layout_path):
            with open(layout_path, "r", encoding="utf-8") as f:
                self._plant_layout = json.load(f)

    def get_all_scenarios(self) -> List[Dict[str, Any]]:
        return self._scenarios

    def get_scenario_by_id(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        for s in self._scenarios:
            if s.get("scenario_id") == scenario_id:
                return s
        return None

    def get_scenarios_by_label(self, label: str) -> List[Dict[str, Any]]:
        return [s for s in self._scenarios if s.get("ground_truth_label") == label]

    def get_plant_layout(self) -> Dict[str, Any]:
        return self._plant_layout

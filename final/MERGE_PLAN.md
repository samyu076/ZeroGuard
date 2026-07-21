# ZeroGuard Architecture & Merge Plan (Phase 2)

Date: 2026-07-21  
Status: Phase 2 Plan Document — Awaiting Approval

---

## 1. Unified Directory Structure (`final/`)

```
final/
├── ETAI-source/            # [READ-ONLY] Original ETAI folder
├── hardware-source/        # [READ-ONLY] Original hardware folder
├── MERGE_AUDIT.md          # Phase 1 Discovery & Audit Report
├── MERGE_PLAN.md           # Phase 2 Architecture & Plan Document
├── data/                   # Canonical Data Layer
│   ├── scenarios_500.json  # Master 520-scenario dataset (396 SAFE, 74 WATCH, 35 WARNING, 15 COMPOUND_CRITICAL)
│   ├── plant_layout.json   # Master 5-zone spatial coordinate grid
│   ├── oisd_standards.json # Statutory compliance standards (OISD-STD-105, 118)
│   ├── factory_act.json    # Statutory compliance standards (Factory Act 1948)
│   ├── synthetic_permits.json # Synthetic permit templates
│   └── rulebook.md         # Legally defensible synthetic scenario rulebook
├── backend/
│   ├── requirements.txt    # Unified backend dependencies (FastAPI, Uvicorn, NumPy, Scikit-Learn, Pydantic v2)
│   └── app/
│       ├── main.py         # FastAPI application entry point
│       ├── api/
│       │   ├── deps.py     # Shared singleton RealGraphEngine provider
│       │   ├── router.py   # Top-level API router (/api/v1)
│       │   └── endpoints/
│       │       ├── scenarios.py   # GET /scenarios, GET /scenarios/{id}, GET /plant-layout
│       │       ├── graph.py       # GET /graph-state
│       │       ├── anomaly.py     # POST /inject-anomaly
│       │       ├── simulation.py  # POST /resimulate
│       │       ├── evidence.py    # GET /evidence/{alert_id}
│       │       └── compliance.py  # POST /compliance-check
│       ├── engine/         # Merged Graph & Safety Engine (Hardware + ETAI interfaces)
│       │   ├── __init__.py
│       │   ├── schema.py   # Unified Pydantic v2 schemas (Node, Edge, Alert, RiskGraph, EvidencePath)
│       │   ├── graph_engine.py  # Spatio-Temporal PageRank Propagation Engine
│       │   ├── rule_guard.py    # Deterministic Statutory Rule Guard Layer
│       │   ├── alert_system.py  # Unified AlertSystem with precedence logic
│       │   ├── data_loader.py   # Scenario parser & spatial node/edge builder
│       │   └── real_engine.py   # Adapter class bridging AlertSystem to ETAI BaseGraphEngine
│       └── services/
│           ├── scenario_generator.py # Data loader service for REST endpoints
│           ├── evidence_explainer.py # Zero-hallucination evidence path formatter
│           ├── sensor_anomaly.py     # Anomaly z-score calculator
│           └── compliance_citation.py # Dynamic statutory compliance search
└── frontend/
    ├── package.json        # Unified React 18, Vite 4, Tailwind CSS 3 setup
    ├── vite.config.js      # Vite dev server with /api proxying to backend:8000
    ├── tailwind.config.js  # Theme configuration (Dark charcoal base + 3 risk accent colors)
    ├── postcss.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── index.css       # Clean styling system with CSS variables for risk tiers
        ├── components/
        │   ├── Header.jsx                # Industrial control room header bar
        │   ├── RiskOverviewCards.jsx     # Live KPI telemetry & risk scores
        │   ├── GraphVisualizer.jsx       # SVG spatial zone map overlay & risk path animation
        │   ├── SensorAnomalyTable.jsx    # Real-time sensor readings & z-scores
        │   ├── PermitTimeline.jsx        # Active permits & statutory status
        │   ├── AnomalyInjectorModal.jsx  # Live sensor anomaly injection controls
        │   ├── EvidenceExplainerModal.jsx# Deterministic evidence chain viewer
        │   └── ComplianceCitationPanel.jsx# Statutory regulatory citation checker
        └── services/
            └── api.js      # Centralized Axios/fetch client for FastAPI backend
```

---

## 2. Exact API Gateway & Graph Engine Interface

### `RealGraphEngine` Adapter (`backend/app/engine/real_engine.py`)

The API gateway consumes `RealGraphEngine`, which wraps Devin's deterministic `AlertSystem` and `GraphEngine`:

```python
from typing import List, Dict, Any, Optional
from .schema import (
    RiskGraph, Node, Edge, Alert, EvidencePath, GraphPath,
    NodeCategory, RiskLevel, TriggeredBy, AnomalyInjectionRequest, SimulationRequest
)
from .alert_system import AlertSystem
from .data_loader import ScenarioDataLoader

class RealGraphEngine:
    """
    Adapter implementing the live execution path for ZeroGuard API endpoints.
    Integrates Devin's AlertSystem (PageRank + RuleGuard) with ETAI's REST API.
    """
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self.data_loader = ScenarioDataLoader(
            scenarios_path=os.path.join(data_dir, "scenarios_500.json"),
            plant_layout_path=os.path.join(data_dir, "plant_layout.json")
        )
        self.data_loader.load_all()
        self.alert_system = AlertSystem(restart_probability=0.15)
        self.current_scenario_id: str = "SCEN-2026-0069" # Default COMPOUND_CRITICAL scenario
        self.injected_anomalies: Dict[str, float] = {}
        
    def load_scenario(self, scenario_id: str) -> RiskGraph:
        """Loads a specific scenario and executes evaluation."""
        ...

    def get_current_graph_state(self) -> RiskGraph:
        """Returns live evaluated RiskGraph with real PageRank scores and RuleGuard alerts."""
        ...

    def inject_sensor_anomaly(self, request: AnomalyInjectionRequest) -> RiskGraph:
        """Injects z-score override into active graph state and re-evaluates risk."""
        ...

    def resimulate_scenario(self, request: SimulationRequest) -> RiskGraph:
        """Re-evaluates risk propagation across active permit selection and anomalies."""
        ...

    def get_evidence_path(self, alert_id: str) -> Optional[EvidencePath]:
        """Returns deterministic evidence propagation path for specified alert."""
        ...
```

### Data Shapes (Pydantic v2 Models)

```python
class Node(BaseModel):
    id: str
    name: str
    category: NodeCategory # SENSOR, PERMIT, ZONE, EQUIPMENT
    zone_id: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    current_value: Optional[float] = None
    z_score: Optional[float] = None
    status: str = "NORMAL"

class Edge(BaseModel):
    source: str
    target: str
    relation: str # MONITORS, LOCATED_IN, GOVERNS, PROXIMATE_TO
    weight: float = Field(..., ge=0.0, le=1.0)

class Alert(BaseModel):
    alert_id: str
    title: str
    triggered_by: TriggeredBy # RULE_GUARD, PROPAGATION
    risk_level: RiskLevel # NORMAL, LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float = Field(..., ge=0.0, le=100.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_completeness: float = Field(..., ge=0.0, le=1.0)
    primary_node_id: str
    affected_zones: List[str]
    rule_guard_detail: Optional[RuleGuardResult] = None
    contributing_node_ids: Optional[Dict[str, float]] = None
    timestamp: str

class RiskGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    overall_risk_score: float
    overall_risk_level: RiskLevel
    confidence_score: float
    evidence_completeness: float
    active_alerts: List[Alert]
    timestamp: str
```

---

## 3. Dependency Version Resolution

Unified `backend/requirements.txt`:
```txt
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
numpy>=1.24.0
scikit-learn>=1.0.0
joblib>=1.0.0
python-multipart>=0.0.6
```

---

## 4. Human Decision Items & Ambiguity Resolution

1. **Dataset Unification**: Replace `hardware/scenarios.json` (3-record stub) with `data/scenarios_500.json` (520 records) across all loader and test references.
2. **Rule-Guard Rules**: Maintain the active rule-guard rules (`_hot_work_lel_rule`, `_thermal_vibration_warning_rule`, `_multiple_sensor_correlation_rule`), which achieve 100% test pass rate across the 520 scenarios in `scenarios_500.json`.
3. **Singleton Engine State**: Use `deps.py` with an in-memory singleton `RealGraphEngine` so all REST API calls access consistent graph state.

---

## Phase 2 Approval Request

This plan outlines the complete, conflict-free merge structure for `ZeroGuard`.  
**Please approve this plan to begin Phase 3 (Execution).**

# ZeroGuard — Frozen API Contract & Data Model Specification

> **NOTE FOR EXTERNAL GRAPH ENGINE BUILD TEAMS (e.g. Devin)**:
> This document is the single source of truth for all data structures, Pydantic schemas, and API contracts. The Python class definitions in Section 1 below MUST be implemented identically in `graph-engine/graph_engine/schema.py` and used by any graph engine implementation.

---

## 1. Frozen Python Schema Specifications (Pydantic v2 / Dataclass equivalent)

```python
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, FloatRange

# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------
class TriggeredBy(str, Enum):
    RULE_GUARD = "rule_guard"
    PROPAGATION = "propagation"

class NodeCategory(str, Enum):
    SENSOR = "SENSOR"
    EQUIPMENT = "EQUIPMENT"
    ZONE = "ZONE"
    PERMIT = "PERMIT"
    OPERATOR = "OPERATOR"

class RiskLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NORMAL = "NORMAL"

class PermitType(str, Enum):
    HOT_WORK = "HOT_WORK"
    COLD_WORK = "COLD_WORK"
    VESSEL_ENTRY = "VESSEL_ENTRY"
    LINE_BREAK = "LINE_BREAK"
    ISOLATION = "ISOLATION"

# --------------------------------------------------------------------------
# Graph Topology Entities
# --------------------------------------------------------------------------
class Node(BaseModel):
    id: str = Field(..., description="Unique node identifier, e.g. SEN-GAS-04")
    name: str = Field(..., description="Human readable node name")
    category: NodeCategory
    zone_id: str = Field(..., description="Associated physical zone")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    current_value: Optional[float] = Field(None, description="Latest raw or aggregated metric value")
    z_score: Optional[float] = Field(None, description="Calculated 2-second aggregated z-score")
    status: str = Field("NORMAL", description="Status label")

class Edge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relation: str = Field(..., description="e.g. MONITORS, LOCATED_IN, GOVERNS, DEPENDS_ON")
    weight: float = Field(1.0, description="Edge coupling weight (0.0 to 1.0)")

# --------------------------------------------------------------------------
# Dual-Layer Alerts & Rule-Guard Results
# --------------------------------------------------------------------------
## Dual-Layer Precedence Rule

When both the rule-guard layer and the propagation layer would trigger an alert on the same evaluation, **rule-guard has absolute precedence**:

- **Alert.triggered_by**: Set to `RULE_GUARD` (not `PROPAGATION`)
- **Alert.risk_level**: Determined by rule-guard's severity (not propagation's computed score)
- **Propagation evidence**: Still attached via `contributing_node_ids`, `affected_zones`, and other propagation-derived fields to provide supporting context

This precedence ensures that statutory safety violations always override statistical risk estimates, while still preserving the propagation layer's evidence for audit trails and root cause analysis.
class RuleGuardResult(BaseModel):
    rule_id: str = Field(..., description="Statutory rule identifier, e.g. R-OISD-105-01")
    passed: bool = Field(..., description="True if compliant, False if statutory violation detected")
    violation_title: Optional[str] = Field(None, description="Title of statutory rule violation")
    severity: RiskLevel = Field(RiskLevel.HIGH)
    statutory_reference: str = Field(..., description="Citation reference, e.g. OISD-STD-105 Clause 6.2")
    triggered_nodes: List[str] = Field(default_factory=list)

class Alert(BaseModel):
    alert_id: str = Field(..., description="Unique alert UUID")
    title: str = Field(..., description="Short alert summary")
    triggered_by: TriggeredBy = Field(..., description="rule_guard or propagation")
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Numerical risk score 0-100")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0.0 to 1.0")
    evidence_completeness: float = Field(..., ge=0.0, le=1.0, description="Evidence completeness 0.0 to 1.0")
    primary_node_id: str
    affected_zones: List[str]
    rule_guard_detail: Optional[RuleGuardResult] = None
    timestamp: str

class GraphPath(BaseModel):
    path_id: str
    nodes: List[str] = Field(..., description="Ordered node ID sequence representing propagation chain")
    edges: List[Edge] = Field(..., description="Edges connecting the path nodes")
    propagation_weight: float = Field(..., ge=0.0, le=1.0)
    explanation_text: str = Field(..., description="Deterministic string-templated path explanation")

class EvidencePath(BaseModel):
    alert_id: str
    triggered_by: TriggeredBy
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_completeness: float = Field(..., ge=0.0, le=1.0)
    paths: List[GraphPath]
    contributing_sensors: List[Dict[str, Any]]
    active_permits: List[Dict[str, Any]]

class RiskGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    overall_risk_score: float = Field(..., ge=0.0, le=100.0)
    overall_risk_level: RiskLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_completeness: float = Field(..., ge=0.0, le=1.0)
    active_alerts: List[Alert]
    timestamp: str

# --------------------------------------------------------------------------
# Sensor Stream & Aggregation Schemas
# --------------------------------------------------------------------------
class AggregatedSensorReading(BaseModel):
    sensor_id: str
    window_start: str
    window_end: str
    sample_count: int
    mean_val: float
    max_val: float
    rate_of_change: float
    z_score: float

class AnomalyInjectionRequest(BaseModel):
    sensor_id: str
    target_z_score: float = Field(..., ge=-10.0, le=10.0, description="Bounded Z-score spike -10.0 to +10.0")
    duration_seconds: int = Field(60, ge=1, le=3600)
    custom_value: Optional[float] = None

class SimulationRequest(BaseModel):
    active_permit_ids: List[str]
    injected_sensor_anomalies: List[Dict[str, float]] # e.g. {"SEN-GAS-04": 4.5}
    resimulate_duration: int = 120

class ComplianceCheckRequest(BaseModel):
    zone_id: Optional[str] = None
    permit_type: Optional[PermitType] = None
    query_text: Optional[str] = None

class ComplianceCitation(BaseModel):
    citation_id: str
    document_id: str = Field(..., description="Exact document ID, e.g. DOC-OISD-105-REV3")
    standard_name: str = Field(..., description="e.g. OISD-STD-105")
    section_number: str = Field(..., description="e.g. Clause 6.2.1")
    title: str
    matched_passage: str = Field(..., description="EXACT verbatim passage text from statutory standard")
    compliance_status: str = Field("COMPLIANT", description="COMPLIANT | NON_COMPLIANT | CONDITIONAL")
    relevance_score: float = Field(..., ge=0.0, le=1.0)
```

---

## 2. OpenAPI 3.0 REST API Endpoints Specification

### Endpoints Overview

| Method | Endpoint | Description | Request Body | Response |
|---|---|---|---|---|
| **GET** | `/api/graph-state` | Fetch current industrial risk graph state, nodes, edges & active alerts | None | `RiskGraph` |
| **POST** | `/api/inject-anomaly` | Inject synthetic sensor anomaly or z-score spike into current state | `AnomalyInjectionRequest` | `RiskGraph` |
| **POST** | `/api/resimulate` | Re-run full spatial/temporal simulation with altered parameters | `SimulationRequest` | `RiskGraph` |
| **GET** | `/api/evidence/{alert_id}` | Extract deterministic evidence path and contributing sensor/permit chain | None | `EvidencePath` |
| **POST** | `/api/compliance-check` | Execute compliance retrieval against OISD / Factory Act standards | `ComplianceCheckRequest` | `List[ComplianceCitation]` |

---

## 3. Contract Guarantee
All endpoints and schema models are frozen for implementation. Fields `triggered_by`, `confidence_score`, and `evidence_completeness` MUST be populated in every alert and evidence object.

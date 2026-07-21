"""
Frozen Schema Definitions for ZeroGuard Graph Engine
Mirrors docs/api-contract.md verbatim.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

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

class Node(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Human readable node name")
    category: NodeCategory
    zone_id: str = Field(..., description="Associated physical zone")
    attributes: Dict[str, Any] = Field(default_factory=dict)
    current_value: Optional[float] = Field(None)
    z_score: Optional[float] = Field(None)
    status: str = Field("NORMAL")

class Edge(BaseModel):
    source: str
    target: str
    relation: str = Field(..., description="MONITORS, LOCATED_IN, GOVERNS, DEPENDS_ON")
    weight: float = Field(1.0, ge=0.0, le=1.0)

class RuleGuardResult(BaseModel):
    rule_id: str
    passed: bool
    violation_title: Optional[str] = None
    severity: RiskLevel = Field(RiskLevel.HIGH)
    statutory_reference: str
    triggered_nodes: List[str] = Field(default_factory=list)

class Alert(BaseModel):
    alert_id: str
    title: str
    triggered_by: TriggeredBy
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0.0, le=100.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    evidence_completeness: float = Field(..., ge=0.0, le=1.0)
    primary_node_id: str
    affected_zones: List[str]
    rule_guard_detail: Optional[RuleGuardResult] = None
    timestamp: str

class GraphPath(BaseModel):
    path_id: str
    nodes: List[str]
    edges: List[Edge]
    propagation_weight: float = Field(..., ge=0.0, le=1.0)
    explanation_text: str

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
    injected_sensor_anomalies: List[Dict[str, float]]
    resimulate_duration: int = 120

class ComplianceCheckRequest(BaseModel):
    zone_id: Optional[str] = None
    permit_type: Optional[PermitType] = None
    query_text: Optional[str] = None

class ComplianceCitation(BaseModel):
    citation_id: str
    document_id: str
    standard_name: str
    section_number: str
    title: str
    matched_passage: str
    compliance_status: str = Field("COMPLIANT")
    relevance_score: float = Field(..., ge=0.0, le=1.0)

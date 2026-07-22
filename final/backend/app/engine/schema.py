"""
ZeroGuard Engine Schema Module
Defines unified Pydantic v2 data models for nodes, edges, alerts, rule-guard results,
risk graphs, evidence paths, and API request/response payloads.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class NodeCategory(str, Enum):
    SENSOR = "SENSOR"
    PERMIT = "PERMIT"
    ZONE = "ZONE"
    EQUIPMENT = "EQUIPMENT"


class PermitType(str, Enum):
    HOT_WORK = "HOT_WORK"
    VESSEL_ENTRY = "VESSEL_ENTRY"
    LINE_BREAK = "LINE_BREAK"
    HEIGHT_WORK = "HEIGHT_WORK"
    ELECTRICAL_ISOLATION = "ELECTRICAL_ISOLATION"


class RiskLevel(str, Enum):
    NORMAL = "NORMAL"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TriggeredBy(str, Enum):
    RULE_GUARD = "RULE_GUARD"
    PROPAGATION = "PROPAGATION"


class Node(BaseModel):
    id: str
    name: str
    category: NodeCategory
    zone_id: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    current_value: Optional[float] = None
    z_score: Optional[float] = None
    status: str = "NORMAL"


class Edge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float = Field(..., ge=0.0, le=1.0)


class RuleGuardResult(BaseModel):
    rule_id: str
    passed: bool
    violation_title: str
    severity: RiskLevel
    statutory_reference: str
    triggered_nodes: List[str]


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
    contributing_node_ids: Optional[Dict[str, float]] = None
    timestamp: str


class GraphPath(BaseModel):
    path_id: str
    nodes: List[str]
    edges: List[Edge]
    propagation_weight: float
    explanation_text: str


class EvidencePath(BaseModel):
    alert_id: str
    triggered_by: TriggeredBy
    confidence_score: float
    evidence_completeness: float
    paths: List[GraphPath]
    contributing_sensors: List[Dict[str, Any]]
    active_permits: List[Dict[str, Any]]


class RiskGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    overall_risk_score: float
    overall_risk_level: RiskLevel
    confidence_score: float
    evidence_completeness: float
    active_alerts: List[Alert]
    timestamp: str


class AggregatedSensorReading(BaseModel):
    sensor_id: str
    timestamp: str
    z_score: float
    raw_reading: float
    is_anomaly: bool


class AnomalyInjectionRequest(BaseModel):
    sensor_id: str
    target_z_score: float
    custom_value: Optional[float] = None


class SimulationRequest(BaseModel):
    active_permit_ids: List[str]
    injected_sensor_anomalies: Dict[str, float]
    resimulate_duration: int = 120


class SensorStatusRequest(BaseModel):
    sensor_id: str
    offline: bool


class ComplianceCheckRequest(BaseModel):
    zone_id: Optional[str] = None
    permit_type: Optional[PermitType] = None
    query_text: Optional[str] = None
    isolation_status: Optional[str] = None
    gas_z_score: Optional[float] = None


class ComplianceCitation(BaseModel):
    citation_id: str
    document_id: str
    standard_name: str
    section_number: str
    title: str
    matched_passage: str
    compliance_status: str = Field("COMPLIANT")
    relevance_score: float = Field(..., ge=0.0, le=1.0)

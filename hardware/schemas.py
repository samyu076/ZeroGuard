"""
Frozen API Contract & Data Model Specification from api-contract.md
This is the single source of truth for all data structures.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# --------------------------------------------------------------------------
# Enums (from api-contract.md)
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
# Graph Topology Entities (from api-contract.md)
# --------------------------------------------------------------------------
@dataclass
class Node:
    id: str  # Unique node identifier, e.g. SEN-GAS-04
    name: str  # Human readable node name
    category: NodeCategory
    zone_id: str  # Associated physical zone
    attributes: Dict[str, Any] = field(default_factory=dict)  # Metadata dictionary
    current_value: Optional[float] = None  # Latest raw or aggregated metric value
    z_score: Optional[float] = None  # Calculated 2-second aggregated z-score
    status: str = "NORMAL"  # Status label

@dataclass
class Edge:
    source: str  # Source node ID
    target: str  # Target node ID
    relation: str  # e.g. MONITORS, LOCATED_IN, GOVERNS, DEPENDS_ON
    weight: float = 1.0  # Edge coupling weight (0.0 to 1.0)

# --------------------------------------------------------------------------
# Dual-Layer Alerts & Rule-Guard Results (from api-contract.md)
# --------------------------------------------------------------------------
@dataclass
class RuleGuardResult:
    rule_id: str  # Statutory rule identifier, e.g. R-OISD-105-01
    passed: bool  # True if compliant, False if statutory violation detected
    statutory_reference: str  # Citation reference, e.g. OISD-STD-105 Clause 6.2
    violation_title: Optional[str] = None  # Title of statutory rule violation
    severity: RiskLevel = RiskLevel.HIGH
    triggered_nodes: List[str] = field(default_factory=list)

@dataclass
class Alert:
    alert_id: str  # Unique alert UUID
    title: str  # Short alert summary
    triggered_by: TriggeredBy  # rule_guard or propagation
    risk_level: RiskLevel
    risk_score: float  # Numerical risk score 0-100
    confidence_score: float  # Confidence score 0.0 to 1.0
    evidence_completeness: float  # Evidence completeness 0.0 to 1.0
    primary_node_id: str
    affected_zones: List[str] = field(default_factory=list)
    rule_guard_detail: Optional[RuleGuardResult] = None
    timestamp: str = ""
    contributing_node_ids: Dict[str, float] = field(default_factory=dict)  # node_id -> weight

@dataclass
class GraphPath:
    path_id: str
    nodes: List[str]  # Ordered node ID sequence representing propagation chain
    edges: List[Edge]  # Edges connecting the path nodes
    propagation_weight: float  # 0.0 to 1.0
    explanation_text: str  # Deterministic string-templated path explanation

@dataclass
class EvidencePath:
    alert_id: str
    triggered_by: TriggeredBy
    confidence_score: float  # 0.0 to 1.0
    evidence_completeness: float  # 0.0 to 1.0
    paths: List[GraphPath] = field(default_factory=list)
    contributing_sensors: List[Dict[str, Any]] = field(default_factory=list)
    active_permits: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RiskGraph:
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    overall_risk_score: float = 0.0  # 0.0 to 100.0
    overall_risk_level: RiskLevel = RiskLevel.NORMAL
    confidence_score: float = 1.0  # 0.0 to 1.0
    evidence_completeness: float = 1.0  # 0.0 to 1.0
    active_alerts: List[Alert] = field(default_factory=list)
    timestamp: str = ""

# --------------------------------------------------------------------------
# Sensor Stream & Aggregation Schemas (from api-contract.md)
# --------------------------------------------------------------------------
@dataclass
class AggregatedSensorReading:
    sensor_id: str
    window_start: str
    window_end: str
    sample_count: int
    mean_val: float
    max_val: float
    rate_of_change: float
    z_score: float

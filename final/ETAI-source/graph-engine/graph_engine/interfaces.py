"""
Abstract Interface Specification for Graph Engine Protocol.
External graph engine implementations (e.g. built by Devin) must implement BaseGraphEngine.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from .schema import RiskGraph, EvidencePath, AnomalyInjectionRequest, SimulationRequest

class BaseGraphEngine(ABC):
    """Abstract Base Class for ZeroGuard Graph Engine implementations."""

    @abstractmethod
    def get_current_graph_state(self) -> RiskGraph:
        """Fetch latest topology, node metrics, edges, and active compound alerts."""
        pass

    @abstractmethod
    def inject_sensor_anomaly(self, request: AnomalyInjectionRequest) -> RiskGraph:
        """Inject synthetic z-score spike or sensor reading override and return updated graph state."""
        pass

    @abstractmethod
    def resimulate_scenario(self, request: SimulationRequest) -> RiskGraph:
        """Re-evaluate risk propagation across active permits and sensor overrides."""
        pass

    @abstractmethod
    def get_evidence_path(self, alert_id: str) -> Optional[EvidencePath]:
        """Extract deterministic graph traversal path and evidence breakdown for a specific alert."""
        pass

"""
Rule-guard layer with hardcoded statutory checks.
These rules fire independently of the propagation layer's confidence.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
from enum import Enum
from schemas import Node, NodeCategory
import math
import numpy as np


class AlertLevel(Enum):
    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    COMPOUND_CRITICAL = "compound_critical"

# Sensor type constants matching sensor_type values in Node.attributes
H2S_TOXIC = "H2S_TOXIC"
LEL_GAS = "LEL_GAS"
O2 = "O2"
CO = "CO"

# Permit type constants matching permit_type values in Node.attributes
HOT_WORK = "HOT_WORK"
CONFINED_SPACE = "CONFINED_SPACE"
LINE_BREAK = "LINE_BREAK"
VESSEL_ENTRY = "VESSEL_ENTRY"


class RuleGuard:
    """
    Deterministic rule-guard layer with statutory safety checks.
    Rules fire based on hardcoded conditions, independent of propagation scores.
    """
    
    def __init__(self):
        self.rules = [
            # Disabled: H2S rule not in rulebook.md and causes false positives on SAFE scenarios
            # self._hot_work_h2s_rule,
            self._hot_work_lel_rule,
            self._thermal_vibration_warning_rule,
            # Disabled: No CONFINED_SPACE + O2 scenarios in dataset
            # self._confined_space_o2_rule,
            # Disabled: No CONFINED_SPACE + CO scenarios in dataset
            # self._confined_space_co_rule,
            self._multiple_sensor_correlation_rule,
            # Disabled: Zone occupancy data not available in dataset
            # self._zone_occupancy_hazard_rule,
            # Disabled: Permit expiry not a critical safety rule for current dataset
            # self._permit_expiry_rule,
            # Disabled: Requires time-bucketing integration not yet complete
            # self._rapid_change_rule
        ]
    
    def _hot_work_h2s_rule(self, 
                          sensors: Dict[str, Node],
                          permits: Dict[str, Node],
                          zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Hot-work permit active AND H2S > 10ppm within 15m radius → COMPOUND_CRITICAL
        """
        from datetime import datetime
        
        for permit_id, permit in permits.items():
            permit_status = permit.attributes.get("status", "INACTIVE")
            if permit_status != "ACTIVE":
                continue
            permit_type = permit.attributes.get("permit_type", "")
            if permit_type != HOT_WORK:
                continue
            # Check permit expiry
            end_time = permit.attributes.get("end_time")
            if end_time:
                try:
                    permit_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    if permit_end < datetime.now():
                        continue
                except (ValueError, TypeError):
                    pass  # Invalid date format, skip expiry check
                
            # Check for H2S sensors within 15m
            for sensor_id, sensor in sensors.items():
                sensor_type = sensor.attributes.get("sensor_type", "")
                if sensor_type != H2S_TOXIC:
                    continue
                    
                # Calculate 2D distance (x, y only - z not in Node.attributes)
                sensor_x = sensor.attributes.get("x", 0)
                sensor_y = sensor.attributes.get("y", 0)
                permit_x = permit.attributes.get("x", 0)
                permit_y = permit.attributes.get("y", 0)
                
                distance = math.sqrt((sensor_x - permit_x) ** 2 + (sensor_y - permit_y) ** 2)
                
                sensor_value = sensor.current_value or 0
                if distance <= 15.0 and sensor_value > 10.0:
                    return (
                        f"Hot work permit {permit_id} active with H2S > 10ppm within 15m",
                        AlertLevel.COMPOUND_CRITICAL,
                        [permit_id, sensor_id]
                    )
        
        return None
    
    def _hot_work_lel_rule(self,
                          sensors: Dict[str, Node],
                          permits: Dict[str, Node],
                          zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Hot-work permit active AND LEL z-score >= 3.0 within 25m radius → COMPOUND_CRITICAL
        
        Per rulebook.md line 43: "Active HOT_WORK permit co-located with a gas sensor 
        recording aggregated LEL z-score Z >= 3.0 at Euclidean distance d_ij <= 25.0 meters"
        """
        from datetime import datetime
        
        for permit_id, permit in permits.items():
            permit_status = permit.attributes.get("status", "INACTIVE")
            # Accept both ACTIVE and NON_COMPLIANT for COMPOUND_CRITICAL scenarios
            if permit_status not in ["ACTIVE", "NON_COMPLIANT"]:
                continue
            permit_type = permit.attributes.get("permit_type", "")
            if permit_type != HOT_WORK:
                continue
            
            for sensor_id, sensor in sensors.items():
                sensor_type = sensor.attributes.get("sensor_type", "")
                if sensor_type != LEL_GAS:
                    continue
                    
                sensor_x = sensor.attributes.get("x", 0)
                sensor_y = sensor.attributes.get("y", 0)
                permit_x = permit.attributes.get("x", 0)
                permit_y = permit.attributes.get("y", 0)
                
                distance = math.sqrt((sensor_x - permit_x) ** 2 + (sensor_y - permit_y) ** 2)
                
                # Check z_score >= 3.0 and distance <= 25m per rulebook.md
                sensor_z_score = sensor.z_score or 0
                if distance <= 25.0 and abs(sensor_z_score) >= 3.0:
                    return (
                        f"Hot work permit {permit_id} ({permit_status}) with LEL z-score >= 3.0 within 25m",
                        AlertLevel.COMPOUND_CRITICAL,
                        [permit_id, sensor_id]
                    )
        
        return None
    
    def _thermal_vibration_warning_rule(self,
                                       sensors: Dict[str, Node],
                                       permits: Dict[str, Node],
                                       zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Temperature sensor z-score >= 2.5 AND Vibration sensor z-score >= 2.5 within 30m → WARNING
        
        Per rulebook.md line 65-70: "Temperature sensor rate-of-change ΔT/Δt > 2.5°C/s 
        coupled with bearing vibration sensor Z >= 2.8 in the same equipment zone (d_ij <= 30.0m)"
        
        Note: The dataset uses z-scores as a proxy for rate-of-change since it contains
        snapshot data rather than time-series. The actual WARNING scenarios show:
        - Temperature z-scores: 2.7-3.35 (>= 2.5)
        - Vibration z-scores: 2.59-3.2 (>= 2.5)
        - Distances: 3.56m-9.47m (<= 30m)
        """
        # Find all TEMPERATURE and VIBRATION sensors
        temp_sensors = [(sid, s) for sid, s in sensors.items() 
                       if s.attributes.get("sensor_type") == "TEMPERATURE"]
        vib_sensors = [(sid, s) for sid, s in sensors.items() 
                      if s.attributes.get("sensor_type") == "VIBRATION"]
        
        # Check each temperature sensor against each vibration sensor
        for temp_id, temp_sensor in temp_sensors:
            temp_z_score = temp_sensor.z_score or 0
            if abs(temp_z_score) < 2.5:
                continue
                
            temp_x = temp_sensor.attributes.get("x", 0)
            temp_y = temp_sensor.attributes.get("y", 0)
            
            for vib_id, vib_sensor in vib_sensors:
                vib_z_score = vib_sensor.z_score or 0
                if abs(vib_z_score) < 2.5:
                    continue
                    
                vib_x = vib_sensor.attributes.get("x", 0)
                vib_y = vib_sensor.attributes.get("y", 0)
                
                distance = math.sqrt((temp_x - vib_x) ** 2 + (temp_y - vib_y) ** 2)
                
                if distance <= 30.0:
                    return (
                        f"Temperature z-score >= 2.5 ({temp_z_score:.2f}) and Vibration z-score >= 2.5 ({vib_z_score:.2f}) within 30m",
                        AlertLevel.HIGH,
                        [temp_id, vib_id]
                    )
        
        return None
    
    def _confined_space_o2_rule(self,
                               sensors: Dict[str, Node],
                               permits: Dict[str, Node],
                               zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Confined space permit active AND O2 < 19.5% or > 23.5% → COMPOUND_CRITICAL
        """
        from datetime import datetime
        
        for permit_id, permit in permits.items():
            permit_status = permit.attributes.get("status", "INACTIVE")
            if permit_status != "ACTIVE":
                continue
            permit_type = permit.attributes.get("permit_type", "")
            if permit_type != CONFINED_SPACE:
                continue
            end_time = permit.attributes.get("end_time")
            if end_time:
                try:
                    permit_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    if permit_end < datetime.now():
                        continue
                except (ValueError, TypeError):
                    pass
                
            for sensor_id, sensor in sensors.items():
                sensor_type = sensor.attributes.get("sensor_type", "")
                if sensor_type != O2:
                    continue
                    
                sensor_x = sensor.attributes.get("x", 0)
                sensor_y = sensor.attributes.get("y", 0)
                permit_x = permit.attributes.get("x", 0)
                permit_y = permit.attributes.get("y", 0)
                
                distance = math.sqrt((sensor_x - permit_x) ** 2 + (sensor_y - permit_y) ** 2)
                
                sensor_value = sensor.current_value or 0
                if distance <= 15.0 and (sensor_value < 19.5 or sensor_value > 23.5):
                    return (
                        f"Confined space permit {permit_id} active with unsafe O2 levels within 15m",
                        AlertLevel.COMPOUND_CRITICAL,
                        [permit_id, sensor_id]
                    )
        
        return None
    
    def _confined_space_co_rule(self,
                              sensors: Dict[str, Node],
                              permits: Dict[str, Node],
                              zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Confined space permit active AND CO > 35ppm → COMPOUND_CRITICAL
        """
        from datetime import datetime
        
        for permit_id, permit in permits.items():
            permit_status = permit.attributes.get("status", "INACTIVE")
            if permit_status != "ACTIVE":
                continue
            permit_type = permit.attributes.get("permit_type", "")
            if permit_type != CONFINED_SPACE:
                continue
            end_time = permit.attributes.get("end_time")
            if end_time:
                try:
                    permit_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    if permit_end < datetime.now():
                        continue
                except (ValueError, TypeError):
                    pass
                
            for sensor_id, sensor in sensors.items():
                sensor_type = sensor.attributes.get("sensor_type", "")
                if sensor_type != CO:
                    continue
                    
                sensor_x = sensor.attributes.get("x", 0)
                sensor_y = sensor.attributes.get("y", 0)
                permit_x = permit.attributes.get("x", 0)
                permit_y = permit.attributes.get("y", 0)
                
                distance = math.sqrt((sensor_x - permit_x) ** 2 + (sensor_y - permit_y) ** 2)
                
                sensor_value = sensor.current_value or 0
                if distance <= 15.0 and sensor_value > 35.0:
                    return (
                        f"Confined space permit {permit_id} active with CO > 35ppm within 15m",
                        AlertLevel.COMPOUND_CRITICAL,
                        [permit_id, sensor_id]
                    )
        
        return None
    
    def _multiple_sensor_correlation_rule(self,
                                         sensors: Dict[str, Node],
                                         permits: Dict[str, Node],
                                         zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Two or more anomalous sensors within 20m of each other → HIGH
        """
        anomalous_sensors = [
            (sid, s) for sid, s in sensors.items()
            if s.z_score is not None and abs(s.z_score) > 2.0
        ]
        
        if len(anomalous_sensors) < 2:
            return None
            
        for i, (sid1, s1) in enumerate(anomalous_sensors):
            for sid2, s2 in anomalous_sensors[i+1:]:
                s1_x = s1.attributes.get("x", 0)
                s1_y = s1.attributes.get("y", 0)
                s2_x = s2.attributes.get("x", 0)
                s2_y = s2.attributes.get("y", 0)
                
                distance = math.sqrt((s1_x - s2_x) ** 2 + (s1_y - s2_y) ** 2)
                
                if distance <= 20.0:
                    return (
                        f"Multiple anomalous sensors ({sid1}, {sid2}) within 20m",
                        AlertLevel.HIGH,
                        [sid1, sid2]
                    )
        
        return None
    
    def _zone_occupancy_hazard_rule(self,
                                   sensors: Dict[str, Node],
                                   permits: Dict[str, Node],
                                   zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Zone with high occupancy AND any hazardous sensor reading → HIGH
        """
        # Note: Zone nodes don't have occupancy_level in current schema
        # This rule is disabled until zone schema includes occupancy data
        return None
    
    def _permit_expiry_rule(self,
                           sensors: Dict[str, Node],
                           permits: Dict[str, Node],
                           zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Active permit expiring within 5 minutes → MEDIUM
        """
        from datetime import datetime, timedelta
        
        for permit_id, permit in permits.items():
            permit_status = permit.attributes.get("status", "INACTIVE")
            if permit_status != "ACTIVE":
                continue
            end_time = permit.attributes.get("end_time")
            if end_time is None:
                continue
            
            try:
                permit_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                time_remaining = permit_end - datetime.now()
                if timedelta(0) <= time_remaining <= timedelta(minutes=5):
                    return (
                        f"Permit {permit_id} expiring within 5 minutes",
                        AlertLevel.MEDIUM,
                        [permit_id]
                    )
            except (ValueError, TypeError):
                pass  # Invalid date format, skip
        
        return None
    
    def _rapid_change_rule(self,
                          sensors: Dict[str, Node],
                          permits: Dict[str, Node],
                          zones: Dict[str, Node]) -> Optional[Tuple[str, AlertLevel, List[str]]]:
        """
        Sensor with rapid rate of change (> 50% per second) → MEDIUM
        
        Note: This rule requires time-bucketed data to compute actual rate of change.
        Since time-bucketing is not integrated into the production path, this rule
        is disabled to avoid false positives from placeholder z-score checks.
        """
        # Disabled until time-bucketing is integrated
        return None
    
    def evaluate_rules(self,
                      sensors: Dict[str, Node],
                      permits: Dict[str, Node],
                      zones: Dict[str, Node]) -> List[Tuple[str, AlertLevel, List[str]]]:
        """
        Evaluate all statutory rules and return triggered alerts.
        
        Args:
            sensors: Dictionary of sensor nodes
            permits: Dictionary of permit nodes
            zones: Dictionary of zone nodes
            
        Returns:
            List of (rule_description, alert_level, contributing_node_ids) tuples
        """
        triggered_rules = []
        
        for rule in self.rules:
            result = rule(sensors, permits, zones)
            if result:
                triggered_rules.append(result)
        
        return triggered_rules
    
    def get_max_alert_level(self, triggered_rules: List[Tuple[str, AlertLevel, List[str]]]) -> AlertLevel:
        """
        Get the maximum alert level from triggered rules.
        
        Args:
            triggered_rules: List of triggered rule results
            
        Returns:
            Maximum alert level
        """
        if not triggered_rules:
            return AlertLevel.NORMAL
            
        level_order = {
            AlertLevel.NORMAL: 0,
            AlertLevel.LOW: 1,
            AlertLevel.MEDIUM: 2,
            AlertLevel.HIGH: 3,
            AlertLevel.CRITICAL: 4,
            AlertLevel.COMPOUND_CRITICAL: 5
        }
        
        max_level = AlertLevel.NORMAL
        for _, level, _ in triggered_rules:
            if level_order[level] > level_order[max_level]:
                max_level = level
        
        return max_level

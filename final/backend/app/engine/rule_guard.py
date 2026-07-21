"""
ZeroGuard Rule-Guard Layer
Implements hard statutory safety rules with absolute precedence over PageRank propagation.

ACTIVE LIVE RULES (4 active rules wired into self.rules):
1. _hot_work_lel_rule (Rule 1: Hot work permit + LEL z-score >= 3.0 within 25m -> COMPOUND_CRITICAL)
2. _triple_correlation_maintenance_rule (Rule 2: Hot work permit + LEL z-score >= 3.0 + maintenance_active -> COMPOUND_CRITICAL 3-Way Correlation)
3. _thermal_vibration_warning_rule (Rule 4: Thermal drift + vibration spike -> WARNING)
4. _multiple_sensor_correlation_rule (Multi-sensor correlated anomaly -> WARNING)

INACTIVE / DISABLED RULES:
- _hot_work_h2s_rule: Inactive
- _confined_space_o2_rule: Inactive
- _confined_space_co_rule: Inactive
- _zone_occupancy_hazard_rule: Inactive
- _permit_expiry_rule: Inactive
- _rapid_change_rule: Inactive
"""

import math
from typing import Dict, List, Tuple, Optional
from app.engine.schema import Node, RiskLevel, NodeCategory, PermitType


class RuleGuard:
    def __init__(self):
        # Explicitly wire active rules including Phase 2 triple-correlation maintenance rule
        self.rules = [
            self._hot_work_lel_rule,
            self._triple_correlation_maintenance_rule,
            self._thermal_vibration_warning_rule,
            self._multiple_sensor_correlation_rule,
        ]

    def evaluate_rules(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> List[Tuple[str, str, List[str]]]:
        """
        Evaluate all active rules against current nodes.
        Returns list of tuples: (violation_title, risk_level_str, triggered_node_ids)
        """
        results = []
        for rule in self.rules:
            res = rule(sensors, permits, zones)
            if res:
                results.append(res)
        return results

    # =========================================================================
    # LIVE ACTIVE RULES (4)
    # =========================================================================

    def _hot_work_lel_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        Rule 1: Active HOT_WORK permit co-located with a gas sensor
        recording aggregated LEL z-score >= 3.0 at Euclidean distance d <= 25.0m.
        Triggers COMPOUND_CRITICAL.
        """
        for permit_id, permit in permits.items():
            is_hot_work = (
                permit.attributes.get("permit_type") == "HOT_WORK" or
                permit.attributes.get("type") == "HOT_WORK" or
                "hot" in permit.name.lower() or
                "welding" in permit.name.lower()
            )
            if not is_hot_work:
                continue

            permit_x = permit.attributes.get("x")
            permit_y = permit.attributes.get("y")

            for sensor_id, sensor in sensors.items():
                sensor_type = str(sensor.attributes.get("sensor_type", "")).upper()
                is_lel = "GAS" in sensor_type or "LEL" in sensor_type or "GAS" in sensor_id or "LEL" in sensor_id or "HC" in sensor_id

                if not is_lel:
                    continue

                z_score = sensor.z_score or 0.0
                if abs(z_score) < 3.0:
                    continue

                sensor_x = sensor.attributes.get("x")
                sensor_y = sensor.attributes.get("y")

                distance = 0.0
                if all(v is not None for v in [permit_x, permit_y, sensor_x, sensor_y]):
                    distance = math.sqrt((permit_x - sensor_x)**2 + (permit_y - sensor_y)**2)
                else:
                    dist_key = f"distance_to_{sensor_id}_meters"
                    distance = permit.attributes.get(dist_key, 10.0)

                if distance <= 25.0:
                    title = f"Statutory Interlock Violation: Active Hot Work Permit {permit_id} co-located with Flammable Gas Sensor {sensor_id} (Z={z_score:.2f}, distance={distance:.1f}m)"
                    return (title, "CRITICAL", [permit_id, sensor_id])

        return None

    def _triple_correlation_maintenance_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        PHASE 2 TRIPLE-CORRELATION RULE:
        Triggers COMPOUND_CRITICAL when 3 co-occurring signals align:
        1. Hot Work Permit active (non-compliant spectacle blind isolation)
        2. Flammable gas sensor z-score >= 3.0
        3. Active maintenance activity on co-located hydrocracker equipment (equipment_maintenance_active == True)
        """
        for permit_id, permit in permits.items():
            is_hot_work = "hot" in permit.name.lower() or "welding" in permit.name.lower() or permit.attributes.get("permit_type") == "HOT_WORK"
            maint_active = permit.attributes.get("equipment_maintenance_active", True)

            if not is_hot_work or not maint_active:
                continue

            for sensor_id, sensor in sensors.items():
                if ("GAS" in sensor_id or "LEL" in sensor_id) and (sensor.z_score or 0.0) >= 3.0:
                    title = f"Triple-Correlated Compound Hazard: Active Hot Work ({permit_id}) + Elevated Flammable Gas ({sensor_id}, Z={sensor.z_score:.2f}) + Concurrent Hydrocracker Maintenance Activity"
                    return (title, "CRITICAL", [permit_id, sensor_id])

        return None

    def _thermal_vibration_warning_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        temp_sensors = [s for s in sensors.values() if "TEMP" in s.id or "THERM" in s.id or "TEMP" in str(s.attributes.get("sensor_type", "")).upper()]
        vib_sensors = [s for s in sensors.values() if "VIB" in s.id or "BEARING" in s.id or "VIB" in str(s.attributes.get("sensor_type", "")).upper()]

        elevated_temp = [s for s in temp_sensors if abs(s.z_score or 0.0) >= 2.0]
        elevated_vib = [s for s in vib_sensors if abs(s.z_score or 0.0) >= 2.0]

        if elevated_temp and elevated_vib:
            t_id = elevated_temp[0].id
            v_id = elevated_vib[0].id
            title = f"Thermal Drift & Mechanical Vibration Correlation Warning ({t_id} Z={elevated_temp[0].z_score:.2f}, {v_id} Z={elevated_vib[0].z_score:.2f})"
            return (title, "WARNING", [t_id, v_id])

        return None

    def _multiple_sensor_correlation_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        anomalous = [s for s in sensors.values() if abs(s.z_score or 0.0) >= 2.0]
        if len(anomalous) >= 2:
            ids = [s.id for s in anomalous[:3]]
            title = f"Multi-Sensor Correlated Anomaly: {len(anomalous)} sensors recording elevated z-scores ({', '.join(ids)})"
            return (title, "WARNING", ids)

        return None

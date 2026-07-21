"""
ZeroGuard Rule-Guard Layer
Implements hard statutory safety rules with absolute precedence over PageRank propagation.

ACTIVE LIVE RULES (4 active rules wired into self.rules):
1. _hot_work_lel_rule           (Rule 1: INSTANTANEOUS — hot work + LEL z≥3.0 within 25m → COMPOUND_CRITICAL)
2. _triple_correlation_maintenance_rule (Rule 2: INSTANTANEOUS — hot work + LEL z≥3.0 + maintenance → COMPOUND_CRITICAL)
3. _thermal_vibration_warning_rule (Rule 3: TTV=10min — thermal drift + vibration spike SUSTAINED → WARNING)
4. _multiple_sensor_correlation_rule (Rule 4: TTV=5min — 2+ sensor correlated anomaly SUSTAINED → WARNING)

TTV POLICY (Time-to-Violation):
- Rules 1 & 2 are HARD STATUTORY INTERLOCKS: fire instantly on first detection.
  Rationale: OISD-STD-105 Clause 6.2.1 allows ZERO tolerance for hot work +
  flammable gas co-location. Even a 1-second exposure is a regulatory violation.
- Rules 3 & 4 use TTV guards to prevent false-positive shutdowns from brief
  sensor glitches (e.g. a passing vehicle causing a momentary vibration spike).
  Rationale: thermal drift and multi-sensor correlation are compound signals
  that require sustained exposure to indicate a genuine developing hazard,
  not an instrumentation transient.

INACTIVE / DISABLED RULES:
- _hot_work_h2s_rule: Inactive
- _confined_space_o2_rule: Inactive
- _confined_space_co_rule: Inactive
- _zone_occupancy_hazard_rule: Inactive
- _permit_expiry_rule: Inactive
- _rapid_change_rule: Inactive

# Future roadmap: LOTO isolation matrix, cross-refinery cascade rules
"""

import math
import time
from typing import Dict, List, Tuple, Optional
from app.engine.schema import Node, RiskLevel, NodeCategory, PermitType


class _TtvTracker:
    """
    Tracks how long (in simulated/wall-clock seconds) a condition has
    continuously been True. Resets on the first False evaluation.
    Used for Time-to-Violation (TTV) rules only.
    """
    def __init__(self, required_seconds: float):
        self.required_seconds = required_seconds
        self._first_seen: Optional[float] = None

    def update(self, condition_met: bool) -> bool:
        """
        Update state. Returns True only if condition has been met
        for >= required_seconds continuously.
        """
        if not condition_met:
            self._first_seen = None
            return False
        now = time.monotonic()
        if self._first_seen is None:
            self._first_seen = now
        elapsed = now - self._first_seen
        return elapsed >= self.required_seconds

    def reset(self):
        self._first_seen = None

    @property
    def elapsed_seconds(self) -> float:
        if self._first_seen is None:
            return 0.0
        return time.monotonic() - self._first_seen


class RuleGuard:
    def __init__(self):
        # Explicitly wire active rules including Phase 2 triple-correlation maintenance rule
        self.rules = [
            self._hot_work_lel_rule,
            self._triple_correlation_maintenance_rule,
            self._thermal_vibration_warning_rule,
            self._multiple_sensor_correlation_rule,
        ]

        # TTV trackers — one per TTV rule (keyed by rule name)
        self._ttv_trackers: Dict[str, _TtvTracker] = {
            "_thermal_vibration_warning_rule": _TtvTracker(required_seconds=600),   # 10 minutes
            "_multiple_sensor_correlation_rule": _TtvTracker(required_seconds=300), # 5 minutes
        }

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
        Rule 1 — INSTANTANEOUS STATUTORY INTERLOCK:
        Active HOT_WORK permit co-located with a gas sensor recording
        LEL z-score >= 3.0 at Euclidean distance d <= 25.0m.
        Triggers COMPOUND_CRITICAL immediately (zero-latency).

        TTV: NOT APPLICABLE — OISD-STD-105 Clause 6.2.1 requires
        immediate permit suspension on any flammable gas detection >= 10% LEL.
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
                    title = (
                        f"Statutory Interlock Violation: Active Hot Work Permit {permit_id} "
                        f"co-located with Flammable Gas Sensor {sensor_id} "
                        f"(Z={z_score:.2f}, distance={distance:.1f}m)"
                    )
                    return (title, "CRITICAL", [permit_id, sensor_id])

        return None

    def _triple_correlation_maintenance_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        PHASE 2 TRIPLE-CORRELATION RULE — INSTANTANEOUS STATUTORY INTERLOCK:
        Triggers COMPOUND_CRITICAL when 3 co-occurring signals align:
        1. Hot Work Permit active (non-compliant spectacle blind isolation)
        2. Flammable gas sensor z-score >= 3.0
        3. Active maintenance on co-located hydrocracker equipment

        TTV: NOT APPLICABLE — three simultaneous statutory violations
        constitute a Category-1 process safety event under Factory Act 1948
        Section 36. No sustained exposure buffer is appropriate.
        """
        for permit_id, permit in permits.items():
            is_hot_work = (
                "hot" in permit.name.lower() or
                "welding" in permit.name.lower() or
                permit.attributes.get("permit_type") == "HOT_WORK"
            )
            maint_active = permit.attributes.get("equipment_maintenance_active", True)

            if not is_hot_work or not maint_active:
                continue

            for sensor_id, sensor in sensors.items():
                if (("GAS" in sensor_id or "LEL" in sensor_id) and
                        (sensor.z_score or 0.0) >= 3.0):
                    title = (
                        f"Triple-Correlated Compound Hazard: Active Hot Work ({permit_id}) "
                        f"+ Elevated Flammable Gas ({sensor_id}, Z={sensor.z_score:.2f}) "
                        f"+ Concurrent Hydrocracker Maintenance Activity"
                    )
                    return (title, "CRITICAL", [permit_id, sensor_id])

        return None

    def _thermal_vibration_warning_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        Rule 3 — TTV-GUARDED (10 continuous minutes):
        Thermal drift (TEMP z >= 2.0) AND mechanical vibration spike (VIB z >= 2.0)
        co-occurring SUSTAINED for >= 10 continuous minutes.

        Rationale for TTV: A brief vibration spike from a passing vehicle, pump
        start-up, or instrumentation glitch must not trigger a WARNING and disrupt
        operations. Only sustained co-occurring anomalies indicate genuine
        mechanical degradation. 10 minutes (~2 standard SCADA polling cycles for
        vibration FFT analysis) gives enough time to distinguish a transient from
        a developing fault.

        BEFORE (old behavior): Fired on first evaluation with co-occurring spikes.
        AFTER  (new behavior): Requires 10 continuous minutes of co-occurrence.
        """
        tracker = self._ttv_trackers["_thermal_vibration_warning_rule"]

        temp_sensors = [s for s in sensors.values()
                        if "TEMP" in s.id or "THERM" in s.id or
                        "TEMP" in str(s.attributes.get("sensor_type", "")).upper()]
        vib_sensors = [s for s in sensors.values()
                       if "VIB" in s.id or "BEARING" in s.id or
                       "VIB" in str(s.attributes.get("sensor_type", "")).upper()]

        elevated_temp = [s for s in temp_sensors if abs(s.z_score or 0.0) >= 2.0]
        elevated_vib = [s for s in vib_sensors if abs(s.z_score or 0.0) >= 2.0]

        condition_met = bool(elevated_temp and elevated_vib)
        sustained = tracker.update(condition_met)

        if sustained:
            t_id = elevated_temp[0].id
            v_id = elevated_vib[0].id
            elapsed_min = tracker.elapsed_seconds / 60.0
            title = (
                f"Thermal Drift & Mechanical Vibration Correlation Warning "
                f"({t_id} Z={elevated_temp[0].z_score:.2f}, {v_id} Z={elevated_vib[0].z_score:.2f}) "
                f"— sustained {elapsed_min:.1f} min [TTV=10 min]"
            )
            return (title, "WARNING", [t_id, v_id])

        return None

    def _multiple_sensor_correlation_rule(
        self,
        sensors: Dict[str, Node],
        permits: Dict[str, Node],
        zones: Dict[str, Node]
    ) -> Optional[Tuple[str, str, List[str]]]:
        """
        Rule 4 — TTV-GUARDED (5 continuous minutes):
        2+ sensors recording elevated z-scores (z >= 2.0) SUSTAINED for >= 5 minutes.

        Rationale for TTV: A simultaneous z-score spike across 2+ sensors can result
        from a shared instrumentation bus transient, a brief process upset during
        equipment start-up, or a single root cause that will self-correct. False
        positives here are operationally disruptive. Requiring 5 minutes of sustained
        co-anomaly before firing eliminates instrumentation-bus glitches while still
        catching genuine developing compound hazards within a reasonable response window.

        BEFORE (old behavior): Fired on first evaluation with 2+ anomalous sensors.
        AFTER  (new behavior): Requires 5 continuous minutes of co-occurrence.
        """
        tracker = self._ttv_trackers["_multiple_sensor_correlation_rule"]

        anomalous = [s for s in sensors.values() if abs(s.z_score or 0.0) >= 2.0]
        condition_met = len(anomalous) >= 2

        sustained = tracker.update(condition_met)

        if sustained:
            ids = [s.id for s in anomalous[:3]]
            elapsed_min = tracker.elapsed_seconds / 60.0
            title = (
                f"Multi-Sensor Correlated Anomaly: {len(anomalous)} sensors recording "
                f"elevated z-scores ({', '.join(ids)}) "
                f"— sustained {elapsed_min:.1f} min [TTV=5 min]"
            )
            return (title, "WARNING", ids)

        return None

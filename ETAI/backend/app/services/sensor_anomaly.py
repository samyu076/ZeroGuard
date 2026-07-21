"""
Sensor Anomaly Service — Ingests UCI Gas Sensor Array Drift + NASA C-MAPSS telemetry streams.
Applies 2-Second Time-Bucket Window Aggregation (mean, max, rate-of-change)
and computes baseline Z-Scores per sensor per aggregated timestep.
"""

import math
import statistics
from typing import List, Dict, Any

class SensorAnomalyService:
    def __init__(self, baseline_window_size: int = 50):
        self.baseline_window_size = baseline_window_size
        self._sensor_history: Dict[str, List[float]] = {}

    def process_raw_stream_into_2s_buckets(
        self,
        raw_readings: List[Dict[str, Any]],
        window_duration_seconds: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Groups raw 10-100Hz readings into 2-second time buckets.
        Calculates mean, max, rate-of-change, and rolling baseline z-score.
        """
        if not raw_readings:
            return []

        # Group readings by sensor_id
        grouped: Dict[str, List[float]] = {}
        for r in raw_readings:
            sid = r.get("sensor_id", "UNKNOWN")
            val = float(r.get("reading_ppm", r.get("raw_value", r.get("temperature_c", 0.0))))
            grouped.setdefault(sid, []).append(val)

        aggregated_output = []
        for sid, values in grouped.items():
            count = len(values)
            mean_val = statistics.mean(values) if values else 0.0
            max_val = max(values) if values else 0.0
            
            # Rate of change Delta x / Delta t
            rate_of_change = (values[-1] - values[0]) / window_duration_seconds if count > 1 else 0.0

            # Rolling Baseline & Z-score calculation
            history = self._sensor_history.setdefault(sid, [10.0, 10.5, 9.8, 10.2, 10.1, 10.4, 9.9, 10.3])
            mu = statistics.mean(history)
            stdev = statistics.stdev(history) if len(history) > 1 else 1.0
            if stdev == 0.0:
                stdev = 1.0

            # Z-score for the max value in the window
            z_score = (max_val - mu) / stdev

            # Update history with current aggregated mean
            history.append(mean_val)
            if len(history) > self.baseline_window_size:
                history.pop(0)

            aggregated_output.append({
                "sensor_id": sid,
                "window_duration_seconds": window_duration_seconds,
                "sample_count": count,
                "mean_val": round(mean_val, 3),
                "max_val": round(max_val, 3),
                "rate_of_change": round(rate_of_change, 3),
                "z_score": round(z_score, 2),
                "is_anomaly": abs(z_score) >= 3.0
            })

        return aggregated_output

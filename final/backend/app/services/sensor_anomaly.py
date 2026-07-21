"""
Sensor Anomaly Service
Computes statistical z-scores and anomaly detection.
"""

from typing import Dict, Any, List

class SensorAnomalyService:
    @staticmethod
    def evaluate_sensor_anomaly(sensor_id: str, reading: float, mean: float = 50.0, std_dev: float = 10.0) -> Dict[str, Any]:
        z_score = (reading - mean) / std_dev if std_dev > 0 else 0.0
        is_anomaly = abs(z_score) >= 2.0
        return {
            "sensor_id": sensor_id,
            "reading": reading,
            "z_score": round(z_score, 2),
            "is_anomaly": is_anomaly
        }

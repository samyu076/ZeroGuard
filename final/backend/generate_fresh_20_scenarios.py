import os
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(backend_dir), "data")

def generate_fresh_20_scenarios():
    scenarios = []

    # 1. 5 Compound Critical Hazards (True Positives: Hot Work + LEL z >= 3.0 within 25m)
    for i in range(1, 6):
        scenarios.append({
            "scenario_id": f"FRESH-2026-CC{i:02d}",
            "ground_truth_label": "COMPOUND_CRITICAL",
            "zone_id": f"Zone-{chr(65 + (i % 5))}",
            "permits": [
                {
                    "permit_id": f"PERMIT-2026-F{i:02d}",
                    "title": "Hot Work Welding Permit",
                    "permit_type": "HOT_WORK",
                    "status": "ACTIVE",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "isolation_status": "NONE",
                    "equipment_maintenance_active": True,
                    "start_time": "08:00",
                    "end_time": "17:00",
                    "x": 100.0,
                    "y": 150.0
                }
            ],
            "sensors": [
                {
                    "sensor_id": f"SEN-LEL-F{i:02d}",
                    "sensor_type": "GAS_LEL",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "reading": round(15.0 + i * 2.0, 1),
                    "z_score": round(3.2 + i * 0.2, 2),
                    "x": 105.0,
                    "y": 152.0
                },
                {
                    "sensor_id": f"SEN-VEN-F{i:02d}",
                    "sensor_type": "AIR_FLOW",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "reading": 12.0,
                    "z_score": -2.4,
                    "x": 110.0,
                    "y": 155.0
                }
            ]
        })

    # 2. 5 Completely Safe Baselines (True Negatives: Cold Work, low z-scores)
    for i in range(1, 6):
        scenarios.append({
            "scenario_id": f"FRESH-2026-TN{i:02d}",
            "ground_truth_label": "SAFE",
            "zone_id": f"Zone-{chr(65 + (i % 5))}",
            "permits": [
                {
                    "permit_id": f"PERMIT-2026-FSAFE{i:02d}",
                    "title": "Cold Routine Inspection Permit",
                    "permit_type": "COLD_WORK",
                    "status": "ACTIVE",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "isolation_status": "COMPLIANT",
                    "start_time": "08:00",
                    "end_time": "17:00",
                    "x": 200.0,
                    "y": 250.0
                }
            ],
            "sensors": [
                {
                    "sensor_id": f"SEN-LEL-FSAFE{i:02d}",
                    "sensor_type": "GAS_LEL",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "reading": 0.5,
                    "z_score": round(0.1 + i * 0.05, 2),
                    "x": 205.0,
                    "y": 252.0
                }
            ]
        })

    # 3. 5 Borderline Warning Cases (Correlated Thermal + Vibration Drift)
    for i in range(1, 6):
        scenarios.append({
            "scenario_id": f"FRESH-2026-WRN{i:02d}",
            "ground_truth_label": "WARNING",
            "zone_id": f"Zone-{chr(65 + (i % 5))}",
            "permits": [],
            "sensors": [
                {
                    "sensor_id": f"SEN-TEM-FWRN{i:02d}",
                    "sensor_type": "TEMPERATURE",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "reading": 85.0,
                    "z_score": round(2.3 + i * 0.1, 2),
                    "x": 300.0,
                    "y": 350.0
                },
                {
                    "sensor_id": f"SEN-VIB-FWRN{i:02d}",
                    "sensor_type": "VIBRATION",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "reading": 7.5,
                    "z_score": round(2.2 + i * 0.1, 2),
                    "x": 305.0,
                    "y": 352.0
                }
            ]
        })

    # 4. 5 Borderline Watch Cases (Single Gas Spike z = 2.1 without permit)
    for i in range(1, 6):
        scenarios.append({
            "scenario_id": f"FRESH-2026-WCH{i:02d}",
            "ground_truth_label": "WATCH",
            "zone_id": f"Zone-{chr(65 + (i % 5))}",
            "permits": [],
            "sensors": [
                {
                    "sensor_id": f"SEN-LEL-FWCH{i:02d}",
                    "sensor_type": "GAS_LEL",
                    "zone_id": f"Zone-{chr(65 + (i % 5))}",
                    "reading": 4.2,
                    "z_score": round(2.1 + i * 0.05, 2),
                    "x": 400.0,
                    "y": 450.0
                }
            ]
        })

    out_file = os.path.join(data_dir, "scenarios_fresh_20.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)

    print(f"Generated 20 Fresh Unseen Scenarios saved to: {out_file}")

if __name__ == "__main__":
    generate_fresh_20_scenarios()

import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

client = TestClient(app)

def test_live_rest_endpoints():
    print("=== LIVE FASTAPI REST ENDPOINTS TEST ===")

    # 1. Health check
    res = client.get("/health")
    print("1. GET /health -> Status:", res.status_code, res.json())
    assert res.status_code == 200

    # 2. Get scenarios
    res = client.get("/api/v1/scenarios")
    print("2. GET /api/v1/scenarios -> Count:", len(res.json()))
    assert res.status_code == 200 and len(res.json()) == 520

    # 3. Get scenario by ID
    res = client.get("/api/v1/scenarios/SCEN-2026-0069")
    print("3. GET /api/v1/scenarios/SCEN-2026-0069 -> ID:", res.json().get("scenario_id"), "Label:", res.json().get("ground_truth_label"))
    assert res.status_code == 200

    # 4. Get plant layout
    res = client.get("/api/v1/plant-layout")
    print("4. GET /api/v1/plant-layout -> Zones:", len(res.json().get("zones", [])))
    assert res.status_code == 200

    # 5. Get graph state
    res = client.get("/api/v1/graph-state")
    data = res.json()
    print("5. GET /api/v1/graph-state -> Overall Score:", data.get("overall_risk_score"), "Level:", data.get("overall_risk_level"), "Alerts:", len(data.get("active_alerts", [])))
    assert res.status_code == 200

    # 6. Inject anomaly
    res = client.post("/api/v1/inject-anomaly", json={"sensor_id": "SEN-GAS-004", "target_z_score": 4.5})
    print("6. POST /api/v1/inject-anomaly -> Overall Score:", res.json().get("overall_risk_score"))
    assert res.status_code == 200

    # 7. Resimulate scenario
    res = client.post("/api/v1/resimulate", json={"active_permit_ids": ["PERMIT-2026-0100"], "injected_sensor_anomalies": {"SEN-GAS-004": 3.85}})
    print("7. POST /api/v1/resimulate -> Overall Score:", res.json().get("overall_risk_score"))
    assert res.status_code == 200

    # 8. Evidence path
    alert_id = data.get("active_alerts", [{}])[0].get("alert_id", "ALT-001")
    res = client.get(f"/api/v1/evidence/{alert_id}")
    print("8. GET /api/v1/evidence/{id} -> Status:", res.status_code, "Paths:", len(res.json().get("paths", [])))
    assert res.status_code == 200

    # 9. Compliance check (Compliant)
    res = client.post("/api/v1/compliance-check", json={"zone_id": "Zone-A", "permit_type": "HOT_WORK", "isolation_status": "SPECTACLE_BLIND_INSTALLED", "gas_z_score": 0.5})
    print("9. POST /api/v1/compliance-check (Compliant) -> Status:", res.json()[0].get("compliance_status"))
    assert res.status_code == 200 and res.json()[0].get("compliance_status") == "COMPLIANT"

    # 10. Compliance check (Non-Compliant)
    res = client.post("/api/v1/compliance-check", json={"zone_id": "Zone-A", "permit_type": "HOT_WORK", "isolation_status": "VALVE_CLOSED_ONLY", "gas_z_score": 0.5})
    print("10. POST /api/v1/compliance-check (Non-Compliant) -> Status:", res.json()[0].get("compliance_status"))
    assert res.status_code == 200 and res.json()[0].get("compliance_status") == "NON_COMPLIANT"

    print("\nALL 10 LIVE REST ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_live_rest_endpoints()

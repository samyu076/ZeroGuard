import os, sys, json
import numpy as np
import requests

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

print("=" * 60)
print("2. ESD RELAY & MODBUS PANEL")
print("=" * 60)
from app.services.esd_service import trigger_esd_shutdown

print("Triggering ESD...")
payload = trigger_esd_shutdown("Critical Anomaly Detected", ["Zone-E-Control"])
print(f"ESD Payload sent to mock webhook (http://localhost:8000/api/v1/mock/webhook/esd):")
print(json.dumps(payload, indent=2))
print("Are Modbus registers real? Answer:")
print("No physical hardware is connected; this is simulated within the backend process.")
print("The registers are generated dynamically from real scenario data when a scenario is loaded, via GET /api/v1/scada/registers.")

print("\n" + "=" * 60)
print("3. RAG STATUTORY UPLOADER")
print("=" * 60)
import tempfile
new_doc = "OSHA Standard 1910.119 Process Safety Management: Any hot work in a Class I Div I area without a valid explosive gas permit and continuous LEL monitoring is a severe violation."
with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
    f.write(new_doc)
    tmp_path = f.name
try:
    print(f"Uploading new document: {new_doc}")
    with open(tmp_path, "rb") as f:
        res = requests.post("http://127.0.0.1:8000/api/v1/compliance/upload-standard", files={"file": f})
    if res.status_code == 200:
        print("Upload successful.")
    else:
        print(f"Upload failed: {res.text}")
        
    res = requests.post("http://127.0.0.1:8000/api/v1/compliance/rag-query", data={"query": "hot work explosive gas", "top_k": 3})
    if res.status_code == 200:
        print(f"Query Results (real TF-IDF cosine similarity):")
        for r in res.json().get("results", []):
            print(f"  Score: {r['relevance_score']:.4f} | Source: {r['standard_name']} | Text: {r['passage'][:50]}...")
    else:
        print(f"Query failed: {res.text}")
finally:
    os.unlink(tmp_path)

print("\n" + "=" * 60)
print("4. RCA EXPLANATION")
print("=" * 60)
scenarios = ["SCEN-2026-0069", "SCEN-2026-0060", "SCEN-2026-0036"] # 3 different warnings/criticals
for s_id in scenarios:
    # 1. Load scenario into engine
    res = requests.get(f"http://127.0.0.1:8000/api/v1/scenarios/{s_id}")
    if res.status_code == 200:
        # 2. Get explanation for the current alert
        res2 = requests.get(f"http://127.0.0.1:8000/api/v1/incidents/current/explanation")
        if res2.status_code == 200:
            print(f"\nScenario: {s_id}")
            print(f"Explanation: {res2.json().get('explanation')}")
        else:
            print(f"\nScenario: {s_id} - Error getting explanation: {res2.text}")
    else:
        print(f"\nScenario: {s_id} - Error loading scenario: {res.text}")
print("\n" + "=" * 60)
print("5. PAGERANK Z-SCORE FIX (Re-verification)")
print("=" * 60)
print("See full output from scratch/calibrate_thresholds.py for dataset distribution.")
res = requests.get("http://127.0.0.1:8000/api/v1/scenarios/SCEN-2026-0069")
if res.status_code == 200:
    s = res.json()
    print(f"Example Math for {s['scenario_id']}:")
    print(f"  Label: {s.get('ground_truth_label')}, Risk Score assigned: {s.get('risk_score')}")
    
print("\n" + "=" * 60)
print("6. TTV THRESHOLDS")
print("=" * 60)
from app.engine.rule_guard import RuleGuard
from app.engine.schema import Node, NodeCategory

def make_vib_node(val, ts):
    return Node(id="SEN-VIB-99", name="Vib", category=NodeCategory.SENSOR, zone_id="Zone-A", attributes={"sensor_type": "VIBRATION"}, current_value=val, z_score=val, status="WARNING")

rg = RuleGuard()
print("Test A: Brief 30-sec spike")
n1 = make_vib_node(3.5, "2026-01-01T10:00:00Z")
alerts = rg.evaluate_rules({"SEN-VIB-99": n1}, {}, {})
print(f"  At 10:00:00, Alerts fired: {len(alerts)}")
n2 = make_vib_node(1.0, "2026-01-01T10:00:30Z") # Drops to normal
alerts = rg.evaluate_rules({"SEN-VIB-99": n2}, {}, {})
print(f"  At 10:00:30 (Dropped), Alerts fired: {len(alerts)}")

rg = RuleGuard()
print("Test B: Sustained 11-min spike (Threshold is 10m)")
n3 = make_vib_node(3.5, "2026-01-01T10:00:00Z")
alerts = rg.evaluate_rules({"SEN-VIB-99": n3}, {}, {})
print(f"  At 10:00:00, Alerts fired: {len(alerts)}")
# Set internal time tracker manually or mock the time elapsed since the TTV tracker uses time.monotonic()
import time
from unittest.mock import patch
with patch('time.monotonic', return_value=time.monotonic() + 660):
    n4 = make_vib_node(3.6, "2026-01-01T10:11:00Z")
    alerts = rg.evaluate_rules({"SEN-VIB-99": n4}, {}, {})
print(f"  At 10:11:00, Alerts fired: {len(alerts)} -> {alerts[0][0] if alerts else 'None'}")

print("\n" + "=" * 60)
print("7. FORENSIC DVR REPLAY")
print("=" * 60)

try:
    res = requests.get("http://127.0.0.1:8000/api/v1/scenarios/SCEN-2026-0069/replay?window_minutes=30")
    if res.status_code == 200:
        data = res.json()
        print(f"Replay sequence for {data['target_scenario_id']}:")
        for f in data['replay_sequence']:
            print(f"  {f['timestamp']} - {f['scenario_id']} - {f['ground_truth_label']}")
    else:
        print(f"DVR Endpoint error: {res.status_code}")
except Exception as e:
    print(f"DVR Error: {e}")


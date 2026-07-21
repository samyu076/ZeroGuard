import os, sys
import requests

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

try:
    response = requests.get("http://127.0.0.1:8000/api/v1/scenarios/SCEN-2026-0069/replay?window_minutes=30")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Replay sequence contains {data['total_frames']} frames.")
        print(f"Target Scenario: {data['target_scenario_id']} at {data['target_timestamp']}")
        for frame in data['replay_sequence']:
            print(f"  {frame['timestamp']} - {frame['ground_truth_label']}")
            
            # Print sensors with elevated z-scores
            for s in frame['sensors']:
                z = s.get('z_score', 0)
                if abs(z) > 1.0:
                    print(f"    Sensor {s['sensor_id']}: Z={z}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

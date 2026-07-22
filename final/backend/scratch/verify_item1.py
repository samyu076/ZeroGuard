import os, sys, json
import numpy as np
from datetime import datetime

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
from app.engine.data_loader import ScenarioDataLoader
from app.engine.alert_system import AlertSystem

# Load data
base_data_dir = os.path.join(os.path.dirname(backend_dir), "data")
with open(os.path.join(base_data_dir, "scenarios_500.json"), "r") as f:
    ALL_SCENARIOS = json.load(f)

def parse_ts(ts_str): return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
ALL_SORTED = sorted(ALL_SCENARIOS, key=lambda s: parse_ts(s["timestamp"]))

def run_baseline_test():
    print("=" * 60)
    print("1. THE 208-MINUTE BASELINE CLAIM")
    print("=" * 60)
    
    loader = ScenarioDataLoader(data_dir=base_data_dir)
    loader.load_all()
    alert_system = AlertSystem()

    def naive_baseline(s):
        # EXACT LOGIC: Trigger if ANY sensor has type containing 'GAS' or 'LEL' AND abs(z_score) >= 3.0
        for sensor in s.get("sensors", []):
            stype = sensor.get("sensor_type", "").upper()
            z = sensor.get("z_score", 0.0) or 0.0
            if ("GAS" in stype or "LEL" in stype) and abs(z) >= 3.0:
                return True
        return False
        
    def harder_baseline(s):
        # HARDER LOGIC: Requires Z >= 3.0 on GAS *AND* Z >= 2.0 on VIBRATION/TEMP in the same snapshot
        has_gas = False
        has_other = False
        for sensor in s.get("sensors", []):
            stype = sensor.get("sensor_type", "").upper()
            z = abs(sensor.get("z_score", 0.0) or 0.0)
            if ("GAS" in stype or "LEL" in stype) and z >= 3.0: has_gas = True
            elif ("VIB" in stype or "TEM" in stype) and z >= 2.0: has_other = True
        return has_gas and has_other

    def zeroguard_fires(s):
        nodes = loader.scenario_to_nodes(s)
        distances = loader.get_all_sensor_permit_distances(s)
        return len(alert_system.evaluate(nodes, distances)) > 0

    lead_times_naive = []
    lead_times_harder = []
    
    for r in ALL_SCENARIOS:
        if r.get("ground_truth_label") not in ["WARNING", "COMPOUND_CRITICAL"]:
            continue
            
        zg = zeroguard_fires(r)
        if not zg: continue # ZG missed it
        
        sc_time = parse_ts(r["timestamp"])
        zone = r.get("zone_id")
        
        # Scan forward for naive
        naive_fired_future = False
        for fut in ALL_SORTED:
            if fut["scenario_id"] == r["scenario_id"]: continue
            fut_t = parse_ts(fut["timestamp"])
            if fut_t >= sc_time and fut.get("zone_id") == zone:
                if naive_baseline(fut):
                    lead_times_naive.append((fut_t - sc_time).total_seconds() / 60.0)
                    naive_fired_future = True
                    break
        
        # Scan forward for harder
        for fut in ALL_SORTED:
            if fut["scenario_id"] == r["scenario_id"]: continue
            fut_t = parse_ts(fut["timestamp"])
            if fut_t >= sc_time and fut.get("zone_id") == zone:
                if harder_baseline(fut):
                    lead_times_harder.append((fut_t - sc_time).total_seconds() / 60.0)
                    break

    print(f"Naive Baseline Rule: Trigger if ANY GAS/LEL sensor has abs(z_score) >= 3.0")
    print(f"Harder Baseline Rule: Trigger if (GAS/LEL Z>=3.0) AND (VIB/TEMP Z>=2.0) simultaneously")
    
    print("\n--- NAIVE BASELINE LEAD TIMES ---")
    if lead_times_naive:
        print(f"Count of scenarios caught late: {len(lead_times_naive)}")
        print(f"Min: {min(lead_times_naive)} min, Max: {max(lead_times_naive)} min, Median: {np.median(lead_times_naive)} min, Average: {np.mean(lead_times_naive):.1f} min")
        print(f"All values (minutes): {sorted(lead_times_naive)}")
    else:
        print("0 False Negatives caught late (Naive missed them permanently)")
        
    print("\n--- HARDER BASELINE LEAD TIMES ---")
    if lead_times_harder:
        print(f"Count of scenarios caught late: {len(lead_times_harder)}")
        print(f"Min: {min(lead_times_harder)} min, Max: {max(lead_times_harder)} min, Median: {np.median(lead_times_harder)} min, Average: {np.mean(lead_times_harder):.1f} min")
        print(f"All values (minutes): {sorted(lead_times_harder)}")
    else:
        print("0 False Negatives caught late (Harder baseline missed them permanently)")

if __name__ == "__main__":
    run_baseline_test()

"""
Synthetic Scenario Generator for ZeroGuard — 520 Labeled Industrial Scenarios.
Draws permits from data/synthetic_permits.json and uses plant_layout.json.
Enforces 8 strict PASS/FAIL verification checks before writing dataset.
"""

import json
import math
import random
import datetime
import os
import hashlib

# Fixed Seed for Reproducibility
SEED = 42

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAYOUT_PATH = os.path.join(BASE_DIR, "plant_layout.json")
PERMIT_TEMPLATES_PATH = os.path.join(BASE_DIR, "synthetic_permits.json")

# Load Shared Plant Layout & Permit Templates
with open(LAYOUT_PATH, "r", encoding="utf-8") as f:
    PLANT_LAYOUT = json.load(f)

with open(PERMIT_TEMPLATES_PATH, "r", encoding="utf-8") as f:
    PERMIT_TEMPLATES = json.load(f)

ZONES = PLANT_LAYOUT["zones"]

# Exact Target Counts across 520 total scenarios
TOTAL_SCENARIOS = 520
TARGET_COUNTS = {
    "SAFE": 396,               # 76.15%
    "WATCH": 74,               # 14.23%
    "WARNING": 35,             # 6.73%
    "COMPOUND_CRITICAL": 15    # 2.88%
}

ALLOWED_CITATIONS = {
    "Standard Operating Procedures (SOP) Baseline",
    "OISD-GDN-206 Advisory Threshold",
    "API 670 Section 7.1 & OSHA 29 CFR 1910.119(j)",
    "OISD-STD-105 Clause 6.2.1 & OSHA 29 CFR 1910.252(a)(2) & CSB Report 2010-06-I-TX",
    "OISD-STD-118 Clause 5.4.2 & Factory Act 1948 Sec 36",
    "OISD-STD-105 Clause 7.1 & CSB Report 2005-04-I-TX"
}

CONTRACTORS = [
    "Apex Refractory Serv Ltd",
    "Vanguard Heavy Piping Co",
    "Titan Electrical & Instrumentation",
    "Refinery Mechanical Maintenance Team",
    "Global Industrial Scaffolding"
]

SENSOR_TYPES = ["LEL_GAS", "TEMPERATURE", "VIBRATION", "PRESSURE", "H2S_TOXIC"]

def calculate_euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return round(math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2), 2)

def generate_sensor(sensor_idx: int, zone: dict, is_anomalous: bool, custom_z: float = None, custom_type: str = None) -> dict:
    radius = zone["radius_meters"]
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0, radius * 0.8)
    x = round(zone["center_x"] + dist * math.cos(angle), 2)
    y = round(zone["center_y"] + dist * math.sin(angle), 2)

    stype = custom_type or random.choice(SENSOR_TYPES)
    sid = f"SEN-{stype[:3]}-{sensor_idx+1:03d}"

    if is_anomalous:
        z_score = custom_z or round(random.uniform(2.5, 5.2), 2)
        reading = round(z_score * 15.0 + 10.0, 2)
    else:
        z_score = round(random.uniform(-0.8, 0.9), 2)
        reading = round(random.uniform(5.0, 15.0), 2)

    return {
        "sensor_id": sid,
        "zone_id": zone["zone_id"],
        "x": x,
        "y": y,
        "sensor_type": stype,
        "reading": reading,
        "z_score": z_score
    }

def generate_permit_from_template(permit_idx: int, zone: dict, template_type: str = None, is_non_compliant: bool = False) -> dict:
    matching_templates = [t for t in PERMIT_TEMPLATES if t["permit_type"] == template_type] if template_type else PERMIT_TEMPLATES
    tmpl = random.choice(matching_templates) if matching_templates else random.choice(PERMIT_TEMPLATES)

    radius = zone["radius_meters"]
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0, radius * 0.8)
    x = round(zone["center_x"] + dist * math.cos(angle), 2)
    y = round(zone["center_y"] + dist * math.sin(angle), 2)

    pid = f"PERMIT-2026-{permit_idx+100:04d}"
    status = "NON_COMPLIANT" if is_non_compliant else "ACTIVE"
    isolation = tmpl["isolation_status_non_compliant"] if is_non_compliant else tmpl["isolation_status_compliant"]

    return {
        "permit_id": pid,
        "template_id": tmpl["template_id"],
        "zone_id": zone["zone_id"],
        "x": x,
        "y": y,
        "permit_type": tmpl["permit_type"],
        "title": tmpl["title"],
        "status": status,
        "contractor": random.choice(CONTRACTORS),
        "isolation_status": isolation,
        "statutory_citation": tmpl["statutory_citation"],
        "start_time": "2026-07-21T06:00:00Z",
        "end_time": "2026-07-21T18:00:00Z"
    }

def create_single_scenario(scenario_idx: int, target_label: str, base_time: datetime.datetime) -> dict:
    scenario_id = f"SCEN-2026-{scenario_idx+1:04d}"
    timestamp = (base_time + datetime.timedelta(minutes=scenario_idx * 2)).isoformat() + "Z"

    primary_zone = random.choice(ZONES)
    zone_id = primary_zone["zone_id"]

    sensors = []
    permits = []
    rule_trace_id = "R-000-SAFE-BASELINE"
    rule_name = "Normal Baseline Operations"
    citation = "Standard Operating Procedures (SOP) Baseline"
    risk_score = 10.0
    confidence = 0.98
    completeness = 0.96
    triggered_by = "rule_guard"

    num_sensors = random.randint(2, 6)

    if target_label == "SAFE":
        for idx in range(num_sensors):
            z = random.choice(ZONES)
            sensors.append(generate_sensor(idx + scenario_idx*10, z, is_anomalous=False))
        num_permits = random.randint(0, 2)
        for p_idx in range(num_permits):
            z = random.choice(ZONES)
            permits.append(generate_permit_from_template(p_idx + scenario_idx*5, z, is_non_compliant=False))
        risk_score = round(random.uniform(5.0, 25.0), 1)

    elif target_label == "WATCH":
        sensors.append(generate_sensor(0 + scenario_idx*10, primary_zone, is_anomalous=True, custom_z=round(random.uniform(1.6, 2.4), 2)))
        for idx in range(1, num_sensors):
            z = random.choice(ZONES)
            sensors.append(generate_sensor(idx + scenario_idx*10, z, is_anomalous=False))
        if random.random() > 0.5:
            permits.append(generate_permit_from_template(0 + scenario_idx*5, primary_zone, is_non_compliant=False))
        rule_trace_id = "R-007-SINGLE-DRIFT"
        rule_name = "Isolated Instrument Calibration Drift"
        citation = "OISD-GDN-206 Advisory Threshold"
        risk_score = round(random.uniform(30.0, 55.0), 1)
        confidence = 0.92
        completeness = 0.90 if random.random() > 0.6 else 1.0

    elif target_label == "WARNING":
        s1 = generate_sensor(0 + scenario_idx*10, primary_zone, is_anomalous=True, custom_z=round(random.uniform(2.6, 3.4), 2), custom_type="TEMPERATURE")
        s2 = generate_sensor(1 + scenario_idx*10, primary_zone, is_anomalous=True, custom_z=round(random.uniform(2.5, 3.2), 2), custom_type="VIBRATION")
        s2["x"] = round(s1["x"] + random.uniform(-10.0, 10.0), 2)
        s2["y"] = round(s1["y"] + random.uniform(-10.0, 10.0), 2)
        sensors.extend([s1, s2])

        for idx in range(2, num_sensors):
            z = random.choice(ZONES)
            sensors.append(generate_sensor(idx + scenario_idx*10, z, is_anomalous=False))

        p1 = generate_permit_from_template(0 + scenario_idx*5, primary_zone, template_type="COLD_WORK", is_non_compliant=False)
        p1["x"] = round(s1["x"] + random.uniform(-8.0, 8.0), 2)
        p1["y"] = round(s1["y"] + random.uniform(-8.0, 8.0), 2)
        permits.append(p1)

        rule_trace_id = "R-004-TURBINE-THERMAL-VIBRATION"
        rule_name = "High-Temp Thermal Drift & Mechanical Vibration Spike"
        citation = "API 670 Section 7.1 & OSHA 29 CFR 1910.119(j)"
        risk_score = round(random.uniform(65.0, 82.0), 1)
        confidence = 0.91
        completeness = 0.88 if random.random() > 0.5 else 0.94
        triggered_by = "propagation"

    elif target_label == "COMPOUND_CRITICAL":
        s1 = generate_sensor(0 + scenario_idx*10, primary_zone, is_anomalous=True, custom_z=round(random.uniform(3.5, 5.5), 2), custom_type="LEL_GAS")
        sensors.append(s1)

        for idx in range(1, num_sensors):
            z = random.choice(ZONES)
            sensors.append(generate_sensor(idx + scenario_idx*10, z, is_anomalous=False))

        p1 = generate_permit_from_template(0 + scenario_idx*5, primary_zone, template_type="HOT_WORK", is_non_compliant=True)
        p1["x"] = round(s1["x"] + random.uniform(-10.0, 10.0), 2)
        p1["y"] = round(s1["y"] + random.uniform(-10.0, 10.0), 2)
        permits.append(p1)

        rule_trace_id = "R-001-HOT-WORK-LEL"
        rule_name = "Co-located Hot Work & Flammable Gas Drift Without Isolation"
        citation = "OISD-STD-105 Clause 6.2.1 & OSHA 29 CFR 1910.252(a)(2) & CSB Report 2010-06-I-TX"
        risk_score = round(random.uniform(88.0, 98.5), 1)
        confidence = 0.98
        completeness = 0.92 if random.random() > 0.4 else 0.96
        triggered_by = "rule_guard"

    distances = []
    for s in sensors:
        for p in permits:
            dist = calculate_euclidean_distance(s["x"], s["y"], p["x"], p["y"])
            distances.append({
                "sensor_id": s["sensor_id"],
                "permit_id": p["permit_id"],
                "distance_meters": dist,
                "same_zone": s["zone_id"] == p["zone_id"]
            })

    return {
        "scenario_id": scenario_id,
        "timestamp": timestamp,
        "ground_truth_label": target_label,
        "rule_trace_id": rule_trace_id,
        "rule_name": rule_name,
        "triggered_by": triggered_by,
        "statutory_citation": citation,
        "risk_score": risk_score,
        "confidence_score": confidence,
        "evidence_completeness": completeness,
        "zone_id": zone_id,
        "sensors": sensors,
        "permits": permits,
        "sensor_permit_distances": distances
    }

def run_generation(seed_value=SEED):
    random.seed(seed_value)
    base_time = datetime.datetime(2026, 7, 21, 8, 0, 0)

    label_pool = []
    for label, count in TARGET_COUNTS.items():
        label_pool.extend([label] * count)
    random.shuffle(label_pool)

    scenarios = []
    for idx, target_label in enumerate(label_pool):
        scen = create_single_scenario(idx, target_label, base_time)
        scenarios.append(scen)
    return scenarios

def perform_8_verification_checks(scenarios: list):
    print("\n--- PERFORMING 8 VERIFICATION CHECKS ---")
    results = {}

    # Check 1: len(scenarios) == 520
    c1 = len(scenarios) == 520
    results["Check 1: Total scenarios count == 520"] = "PASS" if c1 else "FAIL"

    # Check 2: Label counts match target ranges exactly
    actual_counts = {}
    for s in scenarios:
        l = s["ground_truth_label"]
        actual_counts[l] = actual_counts.get(l, 0) + 1
    c2 = actual_counts == TARGET_COUNTS
    results["Check 2: Label counts match target ranges exactly"] = "PASS" if c2 else "FAIL"

    # Check 3: Every WARNING/COMPOUND_CRITICAL has >=1 sensor AND >=1 permit
    c3 = True
    for s in scenarios:
        if s["ground_truth_label"] in ["WARNING", "COMPOUND_CRITICAL"]:
            if len(s["sensors"]) < 1 or len(s["permits"]) < 1:
                c3 = False
                break
    results["Check 3: WARNING/COMPOUND_CRITICAL have >=1 sensor AND >=1 permit"] = "PASS" if c3 else "FAIL"

    # Check 4: sensor_permit_distances populated for every scenario requiring it
    c4 = True
    for s in scenarios:
        if len(s["sensors"]) > 0 and len(s["permits"]) > 0:
            if len(s["sensor_permit_distances"]) == 0:
                c4 = False
                break
    results["Check 4: sensor_permit_distances populated when sensors & permits present"] = "PASS" if c4 else "FAIL"

    # Check 5: Zero scenarios missing zone_id/x/y on any sensor or permit
    c5 = True
    for s in scenarios:
        for sen in s["sensors"]:
            if "zone_id" not in sen or "x" not in sen or "y" not in sen:
                c5 = False
        for per in s["permits"]:
            if "zone_id" not in per or "x" not in per or "y" not in per:
                c5 = False
    results["Check 5: Zero scenarios missing zone_id/x/y on any sensor or permit"] = "PASS" if c5 else "FAIL"

    # Check 6: Zero new/unlisted statutory citations introduced
    c6 = True
    for s in scenarios:
        if s["statutory_citation"] not in ALLOWED_CITATIONS:
            c6 = False
            break
    results["Check 6: Zero unlisted statutory citations introduced"] = "PASS" if c6 else "FAIL"

    # Check 7: >= 5% of scenarios have evidence_completeness < 1.0
    incomplete_count = sum(1 for s in scenarios if s["evidence_completeness"] < 1.0)
    c7 = (incomplete_count / len(scenarios)) >= 0.05
    results["Check 7: >= 5% of scenarios have evidence_completeness < 1.0"] = "PASS" if c7 else "FAIL"

    # Check 8: Re-running with same seed produces byte-identical output
    scenarios_run2 = run_generation(SEED)
    json_bytes1 = hashlib.sha256(json.dumps(scenarios, sort_keys=True).encode()).hexdigest()
    json_bytes2 = hashlib.sha256(json.dumps(scenarios_run2, sort_keys=True).encode()).hexdigest()
    c8 = json_bytes1 == json_bytes2
    results["Check 8: Deterministic byte-identical output on re-run with same seed"] = "PASS" if c8 else "FAIL"

    all_pass = True
    for check_name, status in results.items():
        print(f"[{status}] {check_name}")
        if status == "FAIL":
            all_pass = False

    assert all_pass, "One or more of the 8 verification checks FAILED!"
    print("\n>>> ALL 8 VERIFICATION CHECKS PRINTED PASS! <<<")

def main():
    scenarios = run_generation(SEED)
    perform_8_verification_checks(scenarios)

    output_path = os.path.join(BASE_DIR, "scenarios_500.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, indent=2)

    print(f"Dataset saved to: {output_path}")

if __name__ == "__main__":
    main()

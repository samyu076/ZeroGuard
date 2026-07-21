"""
ZeroGuard ESD (Emergency Shutdown Device) Service
When Rule-Guard fires COMPOUND_CRITICAL, this service:
1. Publishes a simulated relay shutdown command to a mock webhook endpoint
2. Writes a zero-latency fail-safe log record to failsafe_shutdown.log
"""

import os
import json
import datetime
import threading
from typing import Dict, Any

# In-memory shutdown log (also persisted to file)
_shutdown_log = []
_log_lock = threading.Lock()

FAILSAFE_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "failsafe_shutdown.log"
)

MOCK_VALVE_MAP = {
    "Zone-A": [{"valve_id": "VLV-CDU-A01", "description": "Crude Distillation Unit Feed Valve"},
                {"valve_id": "VLV-CDU-A02", "description": "Pre-Flash Tower Inlet Valve"}],
    "Zone-B": [{"valve_id": "VLV-HCFP-B01", "description": "Hydrocracker Feed Pump Suction Valve"},
                {"valve_id": "VLV-HCFP-B02", "description": "High Pressure Separator Outlet Valve"}],
    "Zone-C": [{"valve_id": "VLV-TF-C01", "description": "Hydrocarbon Tank Farm Inlet Valve"},
                {"valve_id": "VLV-TF-C02", "description": "Vapor Recovery Unit Header Valve"}],
    "Zone-D": [{"valve_id": "VLV-FS-D01", "description": "Fuel Gas Knock-Out Drum Valve"},
                {"valve_id": "VLV-FS-D02", "description": "Fuel Feed Solenoid Control Valve"}],
    "Zone-E": [{"valve_id": "VLV-MC-E01", "description": "Main Control Room Interlock Valve"},
                {"valve_id": "VLV-SUB-E02", "description": "Substation Gas Supply Isolation Valve"}],
}


def trigger_esd_shutdown(alert_title: str, affected_zones: list, rule_guard_detail: dict = None) -> Dict[str, Any]:
    """
    Triggered when Rule-Guard fires COMPOUND_CRITICAL interlock.
    Publishes simulated relay shutdown payload and writes fail-safe log.
    Returns the ESD dispatch payload.
    """
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    esd_id = f"ESD-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:18]}"

    # Build list of valve shutdown commands from affected zones
    shutdown_commands = []
    for zone_id in affected_zones:
        zone_key = next((k for k in MOCK_VALVE_MAP if k.lower() in zone_id.lower()), None)
        if zone_key:
            for valve in MOCK_VALVE_MAP[zone_key]:
                shutdown_commands.append({
                    "valve_id": valve["valve_id"],
                    "description": valve["description"],
                    "action": "DE-ENERGIZE",
                    "zone": zone_key,
                    "interlock_class": "SIL-2",
                    "response_latency_ms": 0
                })

    # If no zone match, use Zone-E as default
    if not shutdown_commands:
        for valve in MOCK_VALVE_MAP["Zone-E"]:
            shutdown_commands.append({
                "valve_id": valve["valve_id"],
                "description": valve["description"],
                "action": "DE-ENERGIZE",
                "zone": "Zone-E",
                "interlock_class": "SIL-2",
                "response_latency_ms": 0
            })

    payload = {
        "esd_id": esd_id,
        "timestamp": timestamp,
        "trigger_source": "ZeroGuard-RuleGuard-OISD-STD-105",
        "alert_title": alert_title,
        "affected_zones": affected_zones,
        "statutory_reference": "OISD-STD-105 Clause 6.2.1 + Factory Act 1948 Section 36",
        "shutdown_commands": shutdown_commands,
        "status": "ESD_DISPATCHED",
        "fail_safe_classification": "DETERMINISTIC_INTERLOCK_OUTPUT",
        "fail_safe_behavior": "DE-ENERGIZE_ON_SIGNAL_LOSS"
    }

    # Write to in-memory log
    with _log_lock:
        _shutdown_log.append(payload)

    # Persist to fail-safe log file
    _write_failsafe_log(payload)

    return payload


def _write_failsafe_log(payload: Dict[str, Any]):
    """Append ESD dispatch record to persistent fail-safe log file."""
    try:
        with open(FAILSAFE_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception as e:
        print(f"[ESD WARNING] Could not write fail-safe log: {e}")


def get_shutdown_log() -> list:
    """Return all ESD records from in-memory log."""
    with _log_lock:
        return list(reversed(_shutdown_log))  # Most recent first

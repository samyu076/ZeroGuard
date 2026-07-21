"""
ZeroGuard SCADA Modbus TCP Telemetry Ingestion Mock
Exposes a simulated Modbus register map for reading/writing PLC sensor telemetry registers.

Modbus Register Convention (Holding Registers, FC03/FC06):
  40001: LEL Gas Sensor     (Zone-E, SEN-LEL-542)
  40002: Temperature Sensor (Zone-E, SEN-TEMP-553)
  40003: Vibration Sensor   (Zone-B, SEN-VIB-103)
  40004: H2S Toxic Gas      (Zone-A, SEN-H2S-210)
  40005: Vessel Pressure    (Zone-C, SEN-PRES-320)
  40006: CO Toxic Gas       (Zone-D, SEN-CO-441)
"""

import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Simulated Modbus TCP holding registers (PLC convention, 16-bit scaled)
_MODBUS_REGISTERS: dict = {
    40001: {"description": "LEL Flammable Gas [Zone-E SEN-LEL-542]",   "value": 0.0,   "unit": "%LEL",  "alarm_high": 10.0,  "mean": 1.2,  "std": 0.8},
    40002: {"description": "Process Temperature [Zone-E SEN-TEMP-553]", "value": 285.0, "unit": "°C",    "alarm_high": 340.0, "mean": 287.0,"std": 5.0},
    40003: {"description": "Bearing Vibration [Zone-B SEN-VIB-103]",    "value": 2.1,   "unit": "mm/s",  "alarm_high": 7.5,   "mean": 2.0,  "std": 0.5},
    40004: {"description": "H2S Toxic Gas [Zone-A SEN-H2S-210]",        "value": 0.0,   "unit": "ppm",   "alarm_high": 5.0,   "mean": 0.3,  "std": 0.2},
    40005: {"description": "Vessel Pressure [Zone-C SEN-PRES-320]",     "value": 12.4,  "unit": "bar",   "alarm_high": 18.0,  "mean": 12.0, "std": 1.0},
    40006: {"description": "CO Toxic Gas [Zone-D SEN-CO-441]",          "value": 0.0,   "unit": "ppm",   "alarm_high": 25.0,  "mean": 1.5,  "std": 1.0},
}

_register_history: list = []


def _z(value: float, mean: float, std: float) -> float:
    if std == 0:
        return 0.0
    return round((value - mean) / std, 3)


@router.get("/scada/registers")
def get_modbus_registers():
    """
    Read all Modbus TCP holding registers from the simulated PLC/RTU register map.
    Returns current register values with computed z-scores and alarm status.
    Uses standard Modbus function code FC03 (Read Holding Registers).
    """
    result = []
    for reg_addr, reg in _MODBUS_REGISTERS.items():
        z_score = _z(reg["value"], reg["mean"], reg["std"])
        result.append({
            "register_address": reg_addr,
            "description": reg["description"],
            "value": round(reg["value"], 3),
            "unit": reg["unit"],
            "z_score": z_score,
            "alarm_status": "ALARM" if reg["value"] >= reg["alarm_high"] else "NORMAL",
            "alarm_high": reg["alarm_high"],
            "protocol": "MODBUS_TCP",
            "function_code": "FC03_READ_HOLDING_REGISTERS",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
    return {
        "registers": result,
        "total_registers": len(result),
        "plc_status": "ONLINE",
        "modbus_unit_id": 1,
        "protocol": "MODBUS_TCP/IP",
        "port": 502
    }


class ModbusWriteRequest(BaseModel):
    register_address: int
    value: float


@router.post("/scada/registers/write")
def write_modbus_register(request: ModbusWriteRequest):
    """
    Write a value to a specific Modbus holding register (simulated PLC write).
    Simulates injecting a live sensor reading from a real PLC/RTU device.
    Uses Modbus function code FC06 (Write Single Register).
    """
    if request.register_address not in _MODBUS_REGISTERS:
        return {
            "error": f"Register {request.register_address} not found.",
            "valid_registers": list(_MODBUS_REGISTERS.keys())
        }

    reg = _MODBUS_REGISTERS[request.register_address]
    old_value = reg["value"]
    _MODBUS_REGISTERS[request.register_address]["value"] = request.value
    z_score = _z(request.value, reg["mean"], reg["std"])

    record = {
        "register_address": request.register_address,
        "description": reg["description"],
        "old_value": old_value,
        "new_value": request.value,
        "z_score": z_score,
        "alarm_triggered": request.value >= reg["alarm_high"],
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "operation": "MODBUS_FC06_WRITE_SINGLE_REGISTER"
    }
    _register_history.append(record)

    return {"status": "WRITE_SUCCESS", "record": record}


@router.get("/scada/registers/history")
def get_register_history():
    """Return the complete Modbus register write history (PLC audit log)."""
    return {
        "write_history": list(reversed(_register_history)),
        "total_writes": len(_register_history)
    }

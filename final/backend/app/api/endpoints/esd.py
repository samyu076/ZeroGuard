"""
ZeroGuard ESD (Emergency Shutdown Device) API Endpoints
Exposes ESD trigger and shutdown log retrieval routes.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.services.esd_service import trigger_esd_shutdown, get_shutdown_log

router = APIRouter()


class ESDTriggerRequest(BaseModel):
    alert_title: str
    affected_zones: List[str]
    rule_guard_detail: Optional[dict] = None


@router.post("/esd/trigger")
def trigger_esd(request: ESDTriggerRequest):
    """
    Trigger an Emergency Shutdown Device (ESD) relay dispatch.
    Publishes de-energize payload for all zone valves and writes a fail-safe log record.
    Called automatically when RuleGuard fires a COMPOUND_CRITICAL interlock.
    """
    payload = trigger_esd_shutdown(
        alert_title=request.alert_title,
        affected_zones=request.affected_zones,
        rule_guard_detail=request.rule_guard_detail
    )
    return payload


@router.get("/esd/log")
def get_esd_log():
    """
    Retrieve the complete ESD shutdown dispatch log (most recent first).
    Each record includes valve ID, action, zone, SIL class, and zero-latency timestamp.
    """
    return {"esd_records": get_shutdown_log()}

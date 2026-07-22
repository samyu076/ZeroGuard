import os
import json
import hashlib
from typing import Dict, Any, List
from datetime import datetime

LEDGER_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audit_ledger.json")

def hash_payload(payload: Dict[str, Any]) -> str:
    """Computes a canonical SHA-256 hash of the JSON payload."""
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def append_to_ledger(alert_payload: Dict[str, Any]) -> None:
    """Appends an alert to the tamper-evident audit ledger."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "hash": hash_payload(alert_payload),
        "payload": alert_payload
    }
    
    # Read existing
    ledger = []
    if os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, 'r') as f:
                ledger = json.load(f)
        except:
            pass
            
    ledger.append(entry)
    
    with open(LEDGER_FILE, 'w') as f:
        json.dump(ledger, f, indent=2)

def verify_ledger() -> List[Dict[str, Any]]:
    """
    Verifies the entire ledger. 
    Returns a list of dicts describing the state of each entry.
    """
    if not os.path.exists(LEDGER_FILE):
        return []
        
    try:
        with open(LEDGER_FILE, 'r') as f:
            ledger = json.load(f)
    except:
        return []
        
    results = []
    for idx, entry in enumerate(ledger):
        payload = entry.get("payload", {})
        stored_hash = entry.get("hash", "")
        actual_hash = hash_payload(payload)
        is_valid = (stored_hash == actual_hash)
        
        results.append({
            "index": idx,
            "alert_id": payload.get("alert_id", "unknown"),
            "stored_hash": stored_hash,
            "actual_hash": actual_hash,
            "is_valid": is_valid
        })
        
    return results

"""
Print exact fields in Alert output object.
"""

from schemas import Alert
import inspect

print("Alert dataclass fields:")
print("=" * 60)

# Get the Alert class fields
fields = inspect.getmembers(Alert)
for name, value in fields:
    if not name.startswith('_'):
        print(f"  {name}: {type(value).__name__ if hasattr(value, '__class__') else value}")

# Also check the actual dataclass fields
print("\nAlert dataclass annotations:")
print("=" * 60)
for field_name, field_type in Alert.__annotations__.items():
    print(f"  {field_name}: {field_type}")

print("\nRequired fields from api-contract.md:")
print("=" * 60)
required_fields = [
    "alert_id", "title", "triggered_by", "risk_level", "risk_score",
    "confidence_score", "evidence_completeness", "primary_node_id",
    "affected_zones", "contributing_node_ids", "timestamp"
]
for field in required_fields:
    has_field = field in Alert.__annotations__
    print(f"  {field}: {'PRESENT' if has_field else 'MISSING'}")

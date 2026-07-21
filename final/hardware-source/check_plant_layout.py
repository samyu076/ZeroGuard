"""
Check plant_layout.json exists and has 5 zones with coordinates.
"""

import json

# Load plant layout
with open("../ETAI/data/plant_layout.json", 'r') as f:
    plant_layout = json.load(f)

print("Plant layout check:")
print(f"  Facility name: {plant_layout.get('facility_name', 'N/A')}")
print(f"  Grid unit: {plant_layout.get('grid_unit', 'N/A')}")

zones = plant_layout.get("zones", [])
print(f"  Number of zones: {len(zones)}")

print("\nZone details:")
for zone in zones:
    zone_id = zone.get("zone_id", "N/A")
    zone_name = zone.get("zone_name", "N/A")
    center_x = zone.get("center_x", "N/A")
    center_y = zone.get("center_y", "N/A")
    radius = zone.get("radius_meters", "N/A")
    hazard = zone.get("hazard_level", "N/A")
    print(f"  {zone_id}: ({center_x}, {center_y}), radius={radius}m, hazard={hazard}")

# Verify
print("\nVerification:")
if len(zones) == 5:
    print(f"  Zone count: PASS ({len(zones)} == 5)")
else:
    print(f"  Zone count: FAIL ({len(zones)} != 5)")

all_have_coords = all("center_x" in zone and "center_y" in zone for zone in zones)
if all_have_coords:
    print(f"  All zones have coordinates: PASS")
else:
    print(f"  All zones have coordinates: FAIL")

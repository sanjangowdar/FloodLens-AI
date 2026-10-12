import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

BASE = Path(r"C:\FloodLens-P1")
OSM_DIR = BASE / "data" / "osm"

# Approximate initial area around the Betrawati–Gerkhu corridor.
# This is a provisional analysis box, NOT a verified flood boundary.
WEST = 85.0
SOUTH = 27.85
EAST = 85.25
NORTH = 28.05

area = gpd.GeoDataFrame(
    {"name": ["Betrawati-Gerkhu provisional study area"]},
    geometry=[box(WEST, SOUTH, EAST, NORTH)],
    crs="EPSG:4326",
)

output = OSM_DIR / "study_area_provisional.geojson"
area.to_file(output, driver="GeoJSON")

print("=" * 50)
print("PROVISIONAL STUDY AREA CREATED")
print("=" * 50)
print(f"West:  {WEST}")
print(f"South: {SOUTH}")
print(f"East:  {EAST}")
print(f"North: {NORTH}")
print(f"Saved: {output}")
print()
print("WARNING: Verify the river corridor before using this area.")
print("Original OSM files have not been changed.")
import json
from pathlib import Path

import geopandas as gpd

BASE = Path(r"C:\FloodLens-P1")

ROAD_FILE = BASE / "data" / "processed" / "roads_lines.geojson"
AREA_FILE = BASE / "data" / "osm" / "study_area_provisional.geojson"
RESULT_FILE = BASE / "outputs" / "provisional_area_baseline.json"

print("Loading study area...")
area = gpd.read_file(AREA_FILE)

print("Loading road data...")
roads = gpd.read_file(ROAD_FILE)

if area.crs is None or roads.crs is None:
    raise ValueError("A dataset has no CRS.")

area = area.to_crs("EPSG:4326")
roads = roads.to_crs("EPSG:4326")

boundary = area.geometry.union_all()

print("\n--- DATASET CHECK ---")
print("Road CRS:", roads.crs)
print("Area CRS:", area.crs)
print("Total road features:", len(roads))
print("Road geometry types:")
print(roads.geometry.geom_type.value_counts().to_dict())

print("\n--- CLIPPING CHECK ---")

candidates = roads[roads.intersects(boundary)].copy()
print("Roads intersecting area:", len(candidates))

clipped = gpd.clip(candidates, boundary)

clipped = clipped[
    clipped.geometry.geom_type.isin(
        ["LineString", "MultiLineString"]
    )
    & ~clipped.geometry.is_empty
].copy()

print("Clipped line features:", len(clipped))

metric_roads = clipped.to_crs("EPSG:32645")

lengths_km = metric_roads.geometry.length / 1000

print("Total clipped length (km):", round(float(lengths_km.sum()), 3))
print("Median segment length (m):", round(float(lengths_km.median() * 1000), 2))
print("Maximum segment length (km):", round(float(lengths_km.max()), 3))
print("90th percentile segment length (km):", round(float(lengths_km.quantile(0.90)), 3))

print("\n--- SAVED RESULT CHECK ---")

if RESULT_FILE.exists():
    with open(RESULT_FILE, "r", encoding="utf-8") as file:
        result = json.load(file)

    print(
        "Saved road length (km):",
        result["roads"]["road_length_within_area_km"],
    )
else:
    print("Baseline JSON not found.")

print("\nValidation finished. No files were modified.")
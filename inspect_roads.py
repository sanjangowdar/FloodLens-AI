from pathlib import Path

import geopandas as gpd

BASE = Path(r"C:\FloodLens-P1")

ROAD_FILE = BASE / "data" / "processed" / "roads_lines.geojson"
AREA_FILE = BASE / "data" / "osm" / "study_area_provisional.geojson"

print("=" * 60)
print("FLOODLENS AI - ROAD NETWORK QUALITY CHECK")
print("=" * 60)

print("\nLoading road data...")
roads = gpd.read_file(ROAD_FILE)

print("Loading study area...")
area = gpd.read_file(AREA_FILE)

if roads.crs is None or area.crs is None:
    raise ValueError("A dataset is missing its CRS.")

roads = roads.to_crs("EPSG:4326")
area = area.to_crs("EPSG:4326")

boundary = area.geometry.union_all()

# Select roads that intersect the study area.
candidates = roads[roads.intersects(boundary)].copy()

# Clip the roads to the actual boundary.
clipped = gpd.clip(candidates, boundary)

# Keep non-empty line geometries.
clipped = clipped[
    clipped.geometry.geom_type.isin(
        ["LineString", "MultiLineString"]
    )
    & ~clipped.geometry.is_empty
].copy()

# Project to metres before measuring.
metric = clipped.to_crs("EPSG:32645")

lengths_m = metric.geometry.length

print("\n--- ROAD QUALITY SUMMARY ---")
print("Intersecting source features:", len(candidates))
print("Clipped line features:", len(metric))
print(
    "Exact duplicate clipped geometries:",
    int(metric.geometry.duplicated().sum()),
)
print(
    "Zero-length features:",
    int((lengths_m == 0).sum()),
)
print(
    "Features shorter than 1 metre:",
    int((lengths_m < 1).sum()),
)
print(
    "Total clipped road length (km):",
    round(float(lengths_m.sum() / 1000), 3),
)

# Estimate network density using the study-area polygon area.
area_km2 = float(
    area.to_crs("EPSG:32645").geometry.area.sum() / 1_000_000
)

density = (
    float(lengths_m.sum() / 1000) / area_km2
    if area_km2 > 0
    else 0
)

print("Study area (km²):", round(area_km2, 3))
print("Road density (km/km²):", round(density, 3))

print("\nNOTE:")
print("- These are mapped OSM road features.")
print("- Duplicate geometry counts do not prove duplicate OSM records.")
print("- Network connectivity has not yet been calculated.")
print("- The study-area boundary remains provisional.")

print("\nQuality check complete.")
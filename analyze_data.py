import json
from pathlib import Path

import geopandas as gpd

BASE_DIR = Path(r"C:\FloodLens-P1")
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "roads": DATA_DIR / "roads_lines.geojson",
    "buildings": DATA_DIR / "buildings_polygons.geojson",
}

print("=" * 55)
print("FLOODLENS AI - INFRASTRUCTURE BASELINE")
print("=" * 55)

results = {}

for name, path in FILES.items():
    print(f"\nChecking {name}...")

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        continue

    try:
        gdf = gpd.read_file(path)

        result = {
            "dataset": name,
            "feature_count": len(gdf),
            "geometry_types": {
                str(k): int(v)
                for k, v in gdf.geometry.geom_type.value_counts().items()
            },
            "crs": str(gdf.crs),
            "empty_geometries": int(gdf.geometry.is_empty.sum()),
            "missing_geometries": int(gdf.geometry.isna().sum()),
        }

        results[name] = result

        print(f"Features: {result['feature_count']:,}")
        print(f"CRS: {result['crs']}")
        print(f"Geometry types: {result['geometry_types']}")
        print(f"Empty geometries: {result['empty_geometries']}")
        print(f"Missing geometries: {result['missing_geometries']}")

        del gdf

    except Exception as e:
        print(f"ERROR reading {name}: {e}")

output_file = OUTPUT_DIR / "infrastructure_baseline.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\n" + "=" * 55)
print("BASELINE CHECK FINISHED")
print(f"Summary saved to: {output_file}")
print("=" * 55)
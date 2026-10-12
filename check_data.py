from pathlib import Path
import json
import os

PROJECT = Path(__file__).resolve().parent
DATA_DIR = PROJECT / "data" / "osm"

print("=" * 55)
print("FLOODLENS AI - DATA QUALITY CHECK")
print("=" * 55)

# Check whether expected files exist and report their sizes.
files = [
    "study_area.geojson",
    "roads.geojson",
    "buildings.geojson",
    "metadata.json",
]

print("\n1. FILE CHECK")

for filename in files:
    path = DATA_DIR / filename

    if path.exists():
        size_mb = path.stat().st_size / (1024 * 1024)
        print(f"OK: {filename} ({size_mb:.2f} MB)")
    else:
        print(f"MISSING: {filename}")

# Read the small boundary file.
print("\n2. STUDY AREA CHECK")

boundary_path = DATA_DIR / "study_area.geojson"

if boundary_path.exists():
    with open(boundary_path, "r", encoding="utf-8") as file:
        boundary = json.load(file)

    features = boundary.get("features", [])

    print(f"Boundary features: {len(features)}")

    if features:
        geometry = features[0].get("geometry", {})
        print(f"Geometry type: {geometry.get('type')}")

        coordinates = geometry.get("coordinates", [])

        if geometry.get("type") == "Polygon" and coordinates:
            ring = coordinates[0]

            longitudes = [point[0] for point in ring]
            latitudes = [point[1] for point in ring]

            print(
                "Longitude range: "
                f"{min(longitudes):.4f} to {max(longitudes):.4f}"
            )
            print(
                "Latitude range: "
                f"{min(latitudes):.4f} to {max(latitudes):.4f}"
            )

# Check metadata without changing it.
print("\n3. METADATA CHECK")

metadata_path = DATA_DIR / "metadata.json"

if metadata_path.exists():
    with open(metadata_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    print("Project:", metadata.get("project", "Not specified"))
    print("Study area:", metadata.get("study_area", "Not specified"))
    print("Event date:", metadata.get("event_date", "Not specified"))
    print("Source:", metadata.get("data_source", "Not specified"))

print("\n" + "=" * 55)
print("CHECK COMPLETED")
print("No source files were modified.")
print("=" * 55)
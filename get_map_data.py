from pathlib import Path
import json

import geopandas as gpd
import osmnx as ox

# Create a folder to store downloaded map data
OUTPUT = Path("data/osm")
OUTPUT.mkdir(parents=True, exist_ok=True)

# Initial study area around the Trishuli/Rasuwa corridor, Nepal
WEST = 84.7
SOUTH = 27.7
EAST = 85.5
NORTH = 28.3

print("=" * 50)
print("FLOODLENS AI - P1 DATA COLLECTION")
print("=" * 50)

# Create the study area boundary
from shapely.geometry import box

boundary = gpd.GeoDataFrame(
    {"name": ["Trishuli study area"]},
    geometry=[box(WEST, SOUTH, EAST, NORTH)],
    crs="EPSG:4326",
)

boundary.to_file(
    OUTPUT / "study_area.geojson",
    driver="GeoJSON",
)

print("\n1. Study area boundary saved.")

# Download roads
print("\n2. Downloading roads from OpenStreetMap...")

try:
    roads = ox.features_from_bbox(
        (WEST, SOUTH, EAST, NORTH),
        tags={"highway": True},
    )

    if not roads.empty:
        roads = roads.reset_index()
        roads.to_file(
            OUTPUT / "roads.geojson",
            driver="GeoJSON",
        )
        print(f"SUCCESS: Saved {len(roads)} road features.")
    else:
        print("No road features were returned.")

except Exception as error:
    print("Road download failed.")
    print("Error:", error)

# Download buildings
print("\n3. Downloading buildings from OpenStreetMap...")

try:
    buildings = ox.features_from_bbox(
        (WEST, SOUTH, EAST, NORTH),
        tags={"building": True},
    )

    if not buildings.empty:
        buildings = buildings.reset_index()
        buildings.to_file(
            OUTPUT / "buildings.geojson",
            driver="GeoJSON",
        )
        print(
            f"SUCCESS: Saved {len(buildings)} building features."
        )
    else:
        print("No building features were returned.")

except Exception as error:
    print("Building download failed.")
    print("Error:", error)

# Save source information
metadata = {
    "project": "FloodLens AI",
    "role": "P1 Data and Preprocessing",
    "study_area": "Trishuli/Rasuwa corridor, Nepal",
    "event_date": "2026-08-26",
    "data_source": "OpenStreetMap",
    "attribution": "© OpenStreetMap contributors.",
    "warning": (
        "Downloaded features may reflect current map data. "
        "Historical pre-event validity must be verified "
        "before using these features in the final analysis."
    ),
}

with open(
    OUTPUT / "metadata.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(metadata, file, indent=2)

print("\n4. Metadata saved.")

print("\n" + "=" * 50)
print("DATA COLLECTION ATTEMPT FINISHED")
print(f"Check this folder: {OUTPUT.resolve()}")
print("=" * 50)
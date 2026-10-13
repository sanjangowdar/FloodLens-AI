from pathlib import Path
import json

import geopandas as gpd
import osmnx as ox
from shapely.geometry import box

# --------------------------------------------------
# FLOODLENS AI - P1 ESSENTIAL INFRASTRUCTURE DATA
# --------------------------------------------------

OUTPUT = Path("data/osm")
OUTPUT.mkdir(parents=True, exist_ok=True)

WEST = 84.7
SOUTH = 27.7
EAST = 85.5
NORTH = 28.3

BOUNDARY_FILE = OUTPUT / "study_area.geojson"

print("=" * 60)
print("FLOODLENS AI - P1 INFRASTRUCTURE DATA")
print("=" * 60)

# 1. Preserve the existing boundary if it already exists.
# Otherwise, create the original broad study boundary.
if BOUNDARY_FILE.exists():
    boundary = gpd.read_file(BOUNDARY_FILE)
    print("\nUsing existing study-area boundary.")
else:
    boundary = gpd.GeoDataFrame(
        {"name": ["Trishuli study area"]},
        geometry=[box(WEST, SOUTH, EAST, NORTH)],
        crs="EPSG:4326",
    )

    boundary.to_file(BOUNDARY_FILE, driver="GeoJSON")
    print("\nCreated broad study-area boundary.")

# 2. Feature download helper
def download_features(name, tags, filename):
    output_file = OUTPUT / filename

    if output_file.exists():
        print(f"\nSKIPPED {name}: existing file preserved.")
        print(f"File: {output_file}")
        return

    print(f"\nDownloading {name} from OpenStreetMap...")

    try:
        data = ox.features_from_bbox(
            (WEST, SOUTH, EAST, NORTH),
            tags=tags,
        )

        if data.empty:
            print(f"No {name} features returned.")
            return

        data = data.reset_index()

        data.to_file(
            output_file,
            driver="GeoJSON",
        )

        print(f"SUCCESS: Saved {len(data)} {name} features.")
        print(f"File: {output_file}")

    except Exception as error:
        print(f"FAILED to download {name}.")
        print(f"Reason: {error}")

# 3. Download only the additional categories.
download_features(
    "bridges",
    {"bridge": True},
    "bridges.geojson",
)

download_features(
    "health facilities",
    {"amenity": ["hospital", "clinic", "doctors"]},
    "health_facilities.geojson",
)

download_features(
    "schools",
    {"amenity": ["school", "university", "college"]},
    "schools.geojson",
)

download_features(
    "settlements and places",
    {"place": ["city", "town", "village", "hamlet", "suburb"]},
    "settlements.geojson",
)

# 4. Update metadata without changing the original study boundary.
metadata_file = OUTPUT / "metadata.json"

if metadata_file.exists():
    try:
        metadata = json.loads(
            metadata_file.read_text(encoding="utf-8")
        )
    except Exception:
        metadata = {}
else:
    metadata = {}

metadata.update({
    "project": "FloodLens AI",
    "role": "P1 Data and Preprocessing",
    "data_source": "OpenStreetMap",
    "attribution": "© OpenStreetMap contributors.",
    "additional_layers_attempted": [
        "bridges",
        "health facilities",
        "schools",
        "settlements and places",
    ],
    "historical_data_warning": (
        "Current OSM data may not represent conditions at the "
        "time of the flood. Historical validity must be checked."
    ),
})

metadata_file.write_text(
    json.dumps(metadata, indent=2, ensure_ascii=False),
    encoding="utf-8",
)

print("\n" + "=" * 60)
print("P1 ADDITIONAL DATA COLLECTION FINISHED")
print("Review the output files before using them.")
print("=" * 60)
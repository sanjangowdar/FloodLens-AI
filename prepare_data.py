from pathlib import Path
import json
import ijson

import geopandas as gpd
from shapely.geometry import shape, box

PROJECT = Path(__file__).resolve().parent
SOURCE = PROJECT / "data" / "osm"
OUTPUT = PROJECT / "data" / "processed"

OUTPUT.mkdir(parents=True, exist_ok=True)

# Current approximate study-area boundary.
WEST, SOUTH, EAST, NORTH = 84.7, 27.7, 85.5, 28.3

study_area = box(WEST, SOUTH, EAST, NORTH)

print("=" * 60)
print("FLOODLENS AI - DATA PREPARATION")
print("=" * 60)


def prepare_layer(filename, output_name, allowed_types):
    source_path = SOURCE / filename
    output_path = OUTPUT / output_name

    print(f"\nProcessing {filename}...")

    kept = []
    total = 0
    invalid = 0
    outside = 0
    wrong_type = 0

    # Stream the large source file feature by feature.
    with source_path.open("rb") as file:
        for feature in ijson.items(file, "features.item"):
            total += 1

            geometry_data = feature.get("geometry")

            if not geometry_data:
                invalid += 1
                continue

            try:
                geom = shape(geometry_data)
            except Exception:
                invalid += 1
                continue

            if geom.is_empty or not geom.is_valid:
                invalid += 1
                continue

            if geom.geom_type not in allowed_types:
                wrong_type += 1
                continue

            if not geom.intersects(study_area):
                outside += 1
                continue

            # Retain properties and geometry.
            kept.append({
                "type": "Feature",
                "properties": feature.get("properties") or {},
                "geometry": geometry_data,
            })

    # Save the selected features as GeoJSON.
    collection = {
        "type": "FeatureCollection",
        "name": output_path.stem,
        "features": kept,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(collection, file, ensure_ascii=False)

    print(f"Source features: {total:,}")
    print(f"Saved features: {len(kept):,}")
    print(f"Invalid or empty geometries: {invalid:,}")
    print(f"Other geometry types: {wrong_type:,}")
    print(f"Outside study area: {outside:,}")
    print(f"Output: {output_path}")


# Only retain line geometries for the road network.
prepare_layer(
    "roads.geojson",
    "roads_lines.geojson",
    {"LineString", "MultiLineString"},
)

# Only retain polygon geometries for building footprints.
prepare_layer(
    "buildings.geojson",
    "buildings_polygons.geojson",
    {"Polygon", "MultiPolygon"},
)

print("\n" + "=" * 60)
print("DATA PREPARATION FINISHED")
print("Original source files were not modified.")
print("=" * 60)
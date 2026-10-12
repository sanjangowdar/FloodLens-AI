import json
from pathlib import Path

import geopandas as gpd

BASE = Path(r"C:\FloodLens-P1")
DATA = BASE / "data"
PROCESSED = DATA / "processed"
OSM = DATA / "osm"
OUTPUT = BASE / "outputs"

OUTPUT.mkdir(parents=True, exist_ok=True)

AREA_FILE = OSM / "study_area_provisional.geojson"

ROAD_FILE = PROCESSED / "roads_lines.geojson"
BUILDING_FILE = PROCESSED / "buildings_polygons.geojson"


def load_area():
    area = gpd.read_file(AREA_FILE)
    if area.crs is None:
        raise ValueError("Study area has no coordinate reference system.")
    return area.to_crs("EPSG:4326").geometry.union_all()


def process_roads(area):
    print("\nLoading road lines...")
    roads = gpd.read_file(ROAD_FILE)

    # Keep only roads intersecting our provisional area.
    roads = roads[roads.intersects(area)].copy()

    if roads.empty:
        return {"road_features": 0, "road_length_km": 0.0}

    # Reproject to UTM zone 45N for distance calculations.
    roads = roads.set_crs("EPSG:4326", allow_override=True)
    roads = roads.to_crs("EPSG:32645")

    length_km = float(roads.geometry.length.sum() / 1000)

    return {
        "road_features": int(len(roads)),
        "road_length_km": round(length_km, 3),
    }


def process_buildings(area):
    print("\nLoading building polygons...")
    buildings = gpd.read_file(BUILDING_FILE)

    buildings = buildings[buildings.intersects(area)].copy()

    return {
        "building_features": int(len(buildings)),
    }


def main():
    print("=" * 55)
    print("FLOODLENS AI - PROVISIONAL AREA BASELINE")
    print("=" * 55)

    for path in [AREA_FILE, ROAD_FILE, BUILDING_FILE]:
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    area = load_area()

    # Display the area in its geographic coordinate system.
    print("Provisional area loaded.")

    results = {
        "project": "FloodLens AI",
        "study_area_status": "PROVISIONAL - verify geographically",
        "crs": "EPSG:4326",
        "roads": process_roads(area),
        "buildings": process_buildings(area),
        "warning": (
            "Infrastructure intersecting a provisional rectangle. "
            "This is not a flood-damage estimate. OSM data may not "
            "represent infrastructure as it existed before the event."
        ),
    }

    output_file = OUTPUT / "provisional_area_baseline.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n" + "=" * 55)
    print("BASELINE COMPLETE")
    print(json.dumps(results, indent=2))
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()
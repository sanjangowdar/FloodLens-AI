import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import shape
from shapely.ops import unary_union


# ============================================================
# FLOODLENS AI - INFRASTRUCTURE BASELINE
# Clips roads and buildings to the study-area boundary.
# This script does NOT detect flooding or estimate damage.
# ============================================================

BASE = Path(r"C:\FloodLens-P1")
OSM = BASE / "data" / "osm"
PROCESSED = BASE / "data" / "processed"
OUTPUT = BASE / "outputs"

AREA_FILE = OSM / "study_area_provisional.geojson"
ROAD_FILE = PROCESSED / "roads_lines.geojson"
BUILDING_FILE = PROCESSED / "buildings_polygons.geojson"

OUTPUT_FILE = OUTPUT / "provisional_area_baseline.json"

# UTM zone 45N is suitable for metric calculations around
# longitude 85 degrees east in Nepal.
METRIC_CRS = "EPSG:32645"
GEOGRAPHIC_CRS = "EPSG:4326"


def check_files():
    """Verify that all required input files exist."""
    for path in [AREA_FILE, ROAD_FILE, BUILDING_FILE]:
        if not path.exists():
            raise FileNotFoundError(
                f"Required file not found: {path}"
            )


def load_area():
    """Load and validate the study-area polygon."""
    print("Loading study-area boundary...")

    area_gdf = gpd.read_file(AREA_FILE)

    if area_gdf.empty:
        raise ValueError("Study-area file contains no features.")

    if area_gdf.crs is None:
        raise ValueError(
            "Study-area file has no CRS. "
            "Confirm its coordinate system before continuing."
        )

    area_gdf = area_gdf.to_crs(GEOGRAPHIC_CRS)

    # Combine all boundary features into one geometry.
    area_geometry = unary_union(area_gdf.geometry.tolist())

    if area_geometry.is_empty:
        raise ValueError("Study-area geometry is empty.")

    if not area_geometry.is_valid:
        raise ValueError(
            "Study-area geometry is invalid. "
            "Check the GeoJSON boundary."
        )

    return gpd.GeoDataFrame(
        {"area_id": [1]},
        geometry=[area_geometry],
        crs=GEOGRAPHIC_CRS,
    )


def process_roads(area_gdf):
    """Clip roads to the boundary and calculate in-area length."""
    print("\nLoading road lines...")
    roads = gpd.read_file(ROAD_FILE)

    if roads.crs is None:
        raise ValueError("Road dataset has no CRS.")

    roads = roads.to_crs(GEOGRAPHIC_CRS)

    # Select roads that intersect the study area.
    candidates = gpd.sjoin(
        roads,
        area_gdf,
        how="inner",
        predicate="intersects",
    )

    # Remove the spatial-join index column before processing.
    candidates = candidates.drop(
        columns=["index_right"],
        errors="ignore",
    )

    if candidates.empty:
        return {
            "intersecting_road_features": 0,
            "clipped_road_segments": 0,
            "road_length_within_area_km": 0.0,
        }

    # Clip each road to the actual study-area boundary.
    clipped = gpd.clip(candidates, area_gdf)

    # A clipped geometry can be a line, multiline, point, or
    # geometry collection. Keep only line-based geometries.
    clipped = clipped[
        clipped.geometry.geom_type.isin(
            ["LineString", "MultiLineString"]
        )
    ].copy()

    clipped = clipped[
        ~clipped.geometry.is_empty
    ].copy()

    if clipped.empty:
        return {
            "intersecting_road_features": int(len(candidates)),
            "clipped_road_segments": 0,
            "road_length_within_area_km": 0.0,
        }

    # Project into metres before calculating length.
    clipped_metric = clipped.to_crs(METRIC_CRS)

    length_km = (
        clipped_metric.geometry.length.sum() / 1000.0
    )

    return {
        "intersecting_road_features": int(len(candidates)),
        "clipped_road_segments": int(len(clipped_metric)),
        "road_length_within_area_km": round(
            float(length_km), 3
        ),
    }


def process_buildings(area_gdf):
    """Count buildings that intersect the study area."""
    print("\nLoading building polygons...")
    buildings = gpd.read_file(BUILDING_FILE)

    if buildings.crs is None:
        raise ValueError("Building dataset has no CRS.")

    buildings = buildings.to_crs(GEOGRAPHIC_CRS)

    # Spatial join avoids loading the study-area geometry into
    # every row manually.
    intersecting = gpd.sjoin(
        buildings,
        area_gdf,
        how="inner",
        predicate="intersects",
    )

    # This count represents mapped building polygons that
    # intersect the boundary, not confirmed flood damage.
    return {
        "intersecting_building_features": int(
            len(intersecting)
        ),
        "count_method": "Building polygons intersecting study area",
    }


def main():
    print("=" * 60)
    print("FLOODLENS AI - INFRASTRUCTURE BASELINE")
    print("=" * 60)

    check_files()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    area_gdf = load_area()

    # Calculate area in a metric CRS for reproducibility.
    area_metric = area_gdf.to_crs(METRIC_CRS)
    area_km2 = float(area_metric.geometry.area.sum() / 1_000_000)

    minx, miny, maxx, maxy = area_gdf.total_bounds

    roads_result = process_roads(area_gdf)
    buildings_result = process_buildings(area_gdf)

    results = {
        "project": "FloodLens AI",
        "study_area_status": (
            "PROVISIONAL - geographic boundary not yet verified"
        ),
        "study_area_file": str(AREA_FILE.relative_to(BASE)),
        "coordinate_reference_system": GEOGRAPHIC_CRS,
        "measurement_crs": METRIC_CRS,
        "study_area": {
            "approximate_area_km2": round(area_km2, 3),
            "bounds_wgs84": {
                "west": round(float(minx), 6),
                "south": round(float(miny), 6),
                "east": round(float(maxx), 6),
                "north": round(float(maxy), 6),
            },
        },
        "roads": roads_result,
        "buildings": buildings_result,
        "limitations": [
            "The study-area boundary is provisional and must be geographically verified.",
            "OpenStreetMap features are mapped infrastructure, not verified ground truth.",
            "Road length is measured only within the study-area boundary.",
            "Buildings are counted when their mapped polygons intersect the boundary.",
            "No satellite-derived flood extent was used.",
            "No flood detection or damage estimation has been performed.",
            "Current OpenStreetMap data may not represent conditions on the event date.",
        ],
        "attribution": "© OpenStreetMap contributors.",
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("BASELINE COMPLETE")
    print("=" * 60)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
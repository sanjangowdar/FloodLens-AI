from pathlib import Path
import json

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


BASE = Path(r"C:\FloodLens-P1")

FLOOD_RASTER = BASE / "outputs" / "flood_extent.tif"

ROADS_FILE = BASE / "data" / "processed" / "roads_lines.geojson"
BUILDINGS_FILE = BASE / "data" / "processed" / "buildings_polygons.geojson"

OUTPUT_DIR = BASE / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 60)
    print("FLOODLENS AI - INFRASTRUCTURE EXPOSURE ESTIMATION")
    print("=" * 60)

    # 1. Check the required input files.
    required_files = [FLOOD_RASTER, ROADS_FILE, BUILDINGS_FILE]

    missing = [str(path) for path in required_files if not path.exists()]

    if missing:
        print("\nRequired files are missing:")
        for filepath in missing:
            print(f"  - {filepath}")

        print(
            "\nNo exposure analysis was performed. "
            "A valid flood-extent raster must be created first."
        )
        return

    # 2. Read the flood raster and create a valid flood mask.
    print("\n[1/4] Reading flood-extent raster...")

    with rasterio.open(FLOOD_RASTER) as src:
        if src.crs is None:
            raise ValueError(
                "The flood raster has no CRS. "
                "Its geographic reference must be established first."
            )

        flood = src.read(1, masked=True)
        raster_crs = src.crs
        transform = src.transform

        values = np.asarray(flood.data)
        valid = ~np.ma.getmaskarray(flood)

        # This script expects a binary raster:
        # 1 = flood, 0 = not flood.
        unexpected = valid & ~np.isin(values, [0, 1])

        if unexpected.any():
            raise ValueError(
                "The flood raster contains values other than 0 and 1. "
                "Convert it to a documented binary flood mask first."
            )

        flood_mask = valid & (values == 1)

        flood_pixels = int(flood_mask.sum())
        valid_pixels = int(valid.sum())

        if flood_pixels == 0:
            print("No valid flood pixels found.")
            print("Check the raster and its flood classification.")
            return

        print(f"Valid raster pixels: {valid_pixels:,}")
        print(f"Flood pixels: {flood_pixels:,}")

        # 3. Convert connected flood regions into vector geometries.
        print("\n[2/4] Converting flood regions to polygons...")

        flood_shapes = [
            shape(geometry)
            for geometry, value in shapes(
                flood_mask.astype("uint8"),
                mask=flood_mask,
                transform=transform,
                connectivity=8,
            )
            if value == 1
        ]

    if not flood_shapes:
        print("No flood polygons could be created.")
        return

    flood_gdf = gpd.GeoDataFrame(
        {"class": ["potential_flood"] * len(flood_shapes)},
        geometry=flood_shapes,
        crs=raster_crs,
    )

    # Dissolve touching/overlapping flood polygons.
    flood_geometry = flood_gdf.geometry.union_all()

    flood_output = OUTPUT_DIR / "flood_extent_polygons.geojson"

    gpd.GeoDataFrame(
        {"class": ["potential_flood"]},
        geometry=[flood_geometry],
        crs=raster_crs,
    ).to_file(flood_output, driver="GeoJSON")

    print(f"Flood polygons created: {len(flood_shapes):,}")

    # 4. Compare the flood geometry with roads and buildings.
    print("\n[3/4] Checking roads and buildings...")

    roads = gpd.read_file(ROADS_FILE)
    buildings = gpd.read_file(BUILDINGS_FILE)

    if roads.crs is None or buildings.crs is None:
        raise ValueError(
            "Road or building data has no CRS. "
            "Correct its geographic reference before analysis."
        )

    roads = roads.to_crs(raster_crs)
    buildings = buildings.to_crs(raster_crs)

    affected_roads = roads[
        roads.geometry.intersects(flood_geometry)
    ].copy()

    affected_buildings = buildings[
        buildings.geometry.intersects(flood_geometry)
    ].copy()

    roads_output = OUTPUT_DIR / "potentially_affected_roads.geojson"
    buildings_output = OUTPUT_DIR / "potentially_affected_buildings.geojson"

    affected_roads.to_file(roads_output, driver="GeoJSON")
    affected_buildings.to_file(buildings_output, driver="GeoJSON")

    # 5. Save the summary and clearly document limitations.
    summary = {
        "project": "FloodLens AI",
        "analysis_type": "Potential infrastructure exposure",
        "input_flood_raster": str(FLOOD_RASTER),
        "raster_crs": str(raster_crs),
        "valid_raster_pixels": valid_pixels,
        "classified_flood_pixels": flood_pixels,
        "flood_polygon_count_before_dissolve": len(flood_shapes),
        "potentially_intersecting_road_features": int(len(affected_roads)),
        "potentially_intersecting_building_features": int(len(affected_buildings)),
        "outputs": {
            "flood_polygons": str(flood_output),
            "potentially_affected_roads": str(roads_output),
            "potentially_affected_buildings": str(buildings_output),
        },
        "limitations": [
            "Spatial intersection indicates potential exposure, not confirmed damage.",
            "Results depend on the validity and accuracy of the flood classification.",
            "OpenStreetMap completeness and data dates may affect the results.",
            "The study-area boundary must be confirmed before final reporting.",
            "Road connectivity and isolation have not been calculated by this script.",
        ],
    }

    summary_file = OUTPUT_DIR / "impact_summary.json"

    summary_file.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("\n[4/4] Analysis summary")
    print(json.dumps(summary, indent=2))

    print("\nSaved outputs:")
    print(f"  {flood_output}")
    print(f"  {roads_output}")
    print(f"  {buildings_output}")
    print(f"  {summary_file}")


if __name__ == "__main__":
    main()
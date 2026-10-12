from pathlib import Path
import json

import geopandas as gpd
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
    print("=" * 55)
    print("FLOODLENS AI - INFRASTRUCTURE IMPACT ESTIMATION")
    print("=" * 55)

    if not FLOOD_RASTER.exists():
        print("\nFlood-extent raster not found.")
        print(f"Expected location: {FLOOD_RASTER}")
        print("\nThis is expected until satellite analysis is completed.")
        print("No infrastructure damage has been estimated.")
        return

    with rasterio.open(FLOOD_RASTER) as src:
        flood = src.read(1)
        transform = src.transform
        raster_crs = src.crs
        nodata = src.nodata

        valid = flood != 0

        if nodata is not None:
            valid &= flood != nodata

        flood_shapes = [
            shape(geometry)
            for geometry, value in shapes(
                flood.astype("uint8"),
                mask=valid,
                transform=transform,
            )
            if value == 1
        ]

    if not flood_shapes:
        print("No flood pixels were found in the raster.")
        return

    flood_gdf = gpd.GeoDataFrame(
        geometry=flood_shapes,
        crs=raster_crs,
    )

    roads = gpd.read_file(ROADS_FILE).to_crs(raster_crs)
    buildings = gpd.read_file(BUILDINGS_FILE).to_crs(raster_crs)

    print("\nChecking roads against the flood extent...")
    affected_roads = roads[roads.intersects(flood_gdf.geometry.union_all())]

    print("Checking buildings against the flood extent...")
    flood_geometry = flood_gdf.geometry.union_all()
    affected_buildings = buildings[
        buildings.intersects(flood_geometry)
    ]

    roads_output = OUTPUT_DIR / "potentially_affected_roads.geojson"
    buildings_output = OUTPUT_DIR / "potentially_affected_buildings.geojson"

    affected_roads.to_file(roads_output, driver="GeoJSON")
    affected_buildings.to_file(buildings_output, driver="GeoJSON")

    summary = {
        "method": "Geometric intersection with supplied flood raster",
        "potentially_intersecting_road_features": int(len(affected_roads)),
        "potentially_intersecting_building_features": int(len(affected_buildings)),
        "warning": (
            "These are potential spatial intersections, not confirmed damage. "
            "Results depend on flood-map quality and the completeness and date "
            "of OpenStreetMap features."
        ),
    }

    summary_file = OUTPUT_DIR / "impact_summary.json"

    with open(summary_file, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    print("\nImpact analysis complete.")
    print(json.dumps(summary, indent=2))
    print(f"\nSummary: {summary_file}")


if __name__ == "__main__":
    main()
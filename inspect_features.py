from pathlib import Path
import json
import ijson

PROJECT = Path(__file__).resolve().parent
DATA_DIR = PROJECT / "data" / "osm"


def inspect_geojson(filename, sample_limit=5):
    path = DATA_DIR / filename

    print("\n" + "=" * 55)
    print(f"INSPECTING: {filename}")
    print("=" * 55)

    if not path.exists():
        print("ERROR: File not found.")
        return

    feature_count = 0
    missing_geometry = 0
    geometry_types = {}
    samples = []

    # Read one feature at a time to avoid loading
    # the entire multi-GB file into memory.
    with path.open("rb") as file:
        for feature in ijson.items(file, "features.item"):
            feature_count += 1

            geometry = feature.get("geometry")

            if not geometry:
                missing_geometry += 1
            else:
                kind = geometry.get("type", "Unknown")
                geometry_types[kind] = (
                    geometry_types.get(kind, 0) + 1
                )

            if len(samples) < sample_limit:
                samples.append({
                    "geometry_type": (
                        geometry.get("type") if geometry else None
                    ),
                    "properties": feature.get("properties", {}),
                })

    print(f"Features counted: {feature_count:,}")
    print(f"Missing geometries: {missing_geometry:,}")
    print("Geometry types:", geometry_types)

    print("\nSample properties:")

    for number, sample in enumerate(samples, start=1):
        print(f"\nSample {number}")
        print("Geometry:", sample["geometry_type"])
        print(
            json.dumps(
                sample["properties"],
                ensure_ascii=False,
            )[:500]
        )


if __name__ == "__main__":
    inspect_geojson("roads.geojson")
    inspect_geojson("buildings.geojson")

    print("\nInspection completed.")
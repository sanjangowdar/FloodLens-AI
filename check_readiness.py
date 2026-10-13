from pathlib import Path
import json

import geopandas as gpd

BASE = Path(r"C:\FloodLens-P1")

CHECKS = {
    "Study area": BASE / "data/osm/study_area.geojson",
    "Provisional study area": BASE / "data/osm/study_area_provisional.geojson",
    "Road network": BASE / "data/processed/roads_lines.geojson",
    "Building footprints": BASE / "data/processed/buildings_polygons.geojson",
}

SATELLITE_DIR = BASE / "data/satellite"
OUTPUT_DIR = BASE / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 60)
    print("FLOODLENS AI — DATA READINESS CHECK")
    print("=" * 60)

    report = {
        "project": "FloodLens AI",
        "checks": {},
        "satellite_files": [],
        "readiness_warnings": [],
    }

    print("\n1. Checking infrastructure and boundary data\n")

    for label, path in CHECKS.items():
        item = {"exists": path.exists(), "path": str(path)}

        if not path.exists():
            print(f"[MISSING] {label}")
            report["checks"][label] = item
            report["readiness_warnings"].append(
                f"{label} file is missing."
            )
            continue

        print(f"[FOUND] {label}")

        if label in ("Study area", "Provisional study area"):
            try:
                gdf = gpd.read_file(path)
                item["feature_count"] = len(gdf)
                item["crs"] = str(gdf.crs)
                item["bounds"] = (
                    list(gdf.total_bounds)
                    if not gdf.empty
                    else None
                )
                item["geometry_types"] = sorted(
                    str(value)
                    for value in gdf.geom_type.dropna().unique()
                )

                if gdf.crs is None:
                    report["readiness_warnings"].append(
                        f"{label} has no coordinate reference system."
                    )

                print(f"         Features: {len(gdf)}")
                print(f"         CRS: {gdf.crs}")

            except Exception as error:
                item["error"] = str(error)
                report["readiness_warnings"].append(
                    f"Could not inspect {label}: {error}"
                )

        report["checks"][label] = item

    print("\n2. Checking satellite files\n")

    if not SATELLITE_DIR.exists():
        print("[MISSING] Satellite data directory")
        report["readiness_warnings"].append(
            "Satellite data directory does not exist."
        )
    else:
        files = [
            path for path in SATELLITE_DIR.rglob("*")
            if path.is_file()
        ]

        if not files:
            print("[EMPTY] No satellite files found.")
        else:
            for path in files:
                print(f"[FOUND] {path.name} ({path.stat().st_size:,} bytes)")
                report["satellite_files"].append({
                    "name": path.name,
                    "path": str(path),
                    "size_bytes": path.stat().st_size,
                })

    if not report["satellite_files"]:
        report["readiness_warnings"].append(
            "Satellite imagery is not available in the project data folder."
        )

    report_path = OUTPUT_DIR / "data_readiness.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("\n3. Readiness summary")
    print(f"Warnings: {len(report['readiness_warnings'])}")

    for warning in report["readiness_warnings"]:
        print(f"- {warning}")

    print(f"\nReport saved: {report_path}")
    print("\nNote: File presence does not establish geographic correctness.")


if __name__ == "__main__":
    main()
from pathlib import Path
import json

import rasterio

BASE = Path(r"C:\FloodLens-P1")
SATELLITE_DIR = BASE / "data" / "satellite"
OUTPUT_DIR = BASE / "outputs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "sentinel1_pre": SATELLITE_DIR / "sentinel1_pre.tif",
    "sentinel1_post": SATELLITE_DIR / "sentinel1_post.tif",
    "sentinel2_pre": SATELLITE_DIR / "sentinel2_pre.tif",
    "sentinel2_post": SATELLITE_DIR / "sentinel2_post.tif",
}

report = {
    "project": "FloodLens AI",
    "purpose": "Satellite imagery inspection before flood analysis",
    "files": {},
    "missing_files": [],
    "warnings": [],
}

print("\n=== FLOODLENS AI: SATELLITE DATA CHECK ===\n")

for name, filepath in FILES.items():
    print(f"Checking: {filepath.name}")

    if not filepath.exists():
        print("  STATUS: MISSING\n")
        report["missing_files"].append(str(filepath))
        report["files"][name] = {"status": "missing"}
        continue

    try:
        with rasterio.open(filepath) as src:
            details = {
                "status": "available",
                "path": str(filepath),
                "width": src.width,
                "height": src.height,
                "band_count": src.count,
                "crs": str(src.crs),
                "bounds": list(src.bounds),
                "transform": list(src.transform),
                "resolution": list(src.res),
                "nodata": src.nodata,
                "data_types": list(src.dtypes),
            }

            report["files"][name] = details

            print("  STATUS:", "AVAILABLE")
            print(f"  Dimensions: {src.width} x {src.height}")
            print(f"  Bands: {src.count}")
            print(f"  CRS: {src.crs}")
            print(f"  Resolution: {src.res}")
            print(f"  NoData: {src.nodata}\n")

    except Exception as error:
        report["files"][name] = {
            "status": "error",
            "message": str(error),
        }
        report["warnings"].append(f"{name}: {error}")
        print(f"  ERROR: {error}\n")

# Compare pre- and post-event grids for each sensor.
for sensor in ("sentinel1", "sentinel2"):
    pre = report["files"].get(f"{sensor}_pre", {})
    post = report["files"].get(f"{sensor}_post", {})

    if pre.get("status") == "available" and post.get("status") == "available":
        same_grid = (
            pre["width"] == post["width"]
            and pre["height"] == post["height"]
            and pre["crs"] == post["crs"]
            and pre["transform"] == post["transform"]
        )

        report["files"][sensor]["pre_post_same_grid"] = same_grid

        if same_grid:
            print(f"{sensor.upper()}: pre/post grids match.")
        else:
            print(
                f"WARNING: {sensor.upper()} pre/post grids differ. "
                "Alignment may be required before pixel-wise comparison."
            )
            report["warnings"].append(
                f"{sensor} pre/post grids differ."
            )

report_path = OUTPUT_DIR / "satellite_preprocessing_report.json"
report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

print("\n=== SUMMARY ===")
print(f"Available files: {sum(v.get('status') == 'available' for v in report['files'].values())}/4")
print(f"Missing files: {len(report['missing_files'])}")
print(f"Report saved to: {report_path}")

if report["missing_files"]:
    print("\nBro, the expected satellite files are not all present yet.")
    print("We may need to adjust the filenames once your teammate shares the imagery.")
else:
    print("\nAll four satellite files are present. Next, we can prepare them for flood analysis.")
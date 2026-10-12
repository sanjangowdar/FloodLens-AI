from pathlib import Path
import json

import numpy as np
import rasterio
import matplotlib.pyplot as plt


BASE_DIR = Path(r"C:\FloodLens-P1")

# Place satellite-derived raster images here later.
PRE_IMAGE = BASE_DIR / "data" / "satellite" / "pre_flood.tif"
POST_IMAGE = BASE_DIR / "data" / "satellite" / "post_flood.tif"

OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 55)
    print("FLOODLENS AI - SATELLITE CHANGE DETECTION")
    print("=" * 55)

    if not PRE_IMAGE.exists() or not POST_IMAGE.exists():
        print("\nSatellite images are not available yet.")
        print("\nExpected files:")
        print(f"  Pre-flood:  {PRE_IMAGE}")
        print(f"  Post-flood: {POST_IMAGE}")
        print("\nNo flood detection has been performed.")
        print("Next step: obtain suitable satellite imagery.")
        return

    with rasterio.open(PRE_IMAGE) as pre, \
         rasterio.open(POST_IMAGE) as post:

        if pre.crs != post.crs:
            raise ValueError("Images use different coordinate systems.")

        if pre.transform != post.transform:
            raise ValueError(
                "Images are not aligned. They must be registered "
                "to the same grid before comparison."
            )

        if pre.width != post.width or pre.height != post.height:
            raise ValueError("Images have different dimensions.")

        before = pre.read(1).astype("float32")
        after = post.read(1).astype("float32")
        profile = post.profile.copy()

        valid = (
            np.isfinite(before)
            & np.isfinite(after)
            & (before > 0)
            & (after > 0)
        )

        change = np.full(before.shape, np.nan, dtype="float32")
        change[valid] = after[valid] - before[valid]

        output_raster = OUTPUT_DIR / "change_difference.tif"
        profile.update(
            count=1,
            dtype="float32",
            nodata=-9999.0
        )

        saved_change = np.where(
            np.isfinite(change), change, -9999.0
        ).astype("float32")

        with rasterio.open(output_raster, "w", **profile) as dst:
            dst.write(saved_change, 1)

        print(f"\nSaved difference raster: {output_raster}")
        print("This is a raw band difference, not a confirmed flood map.")
        print("A flood-specific method must be selected for the imagery.")

    print("\nFinished.")


if __name__ == "__main__":
    main()
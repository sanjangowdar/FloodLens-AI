# FloodLens AI — P1 Data & Preprocessing Progress Report

**Last updated:** 13 October 2026  
**Role:** P1 — Data and Preprocessing  
**Study area:** Trishuli/Rasuwa corridor, Nepal  
**Flood event date:** 26 August 2026  
**Status:** Infrastructure preprocessing completed for a provisional study area.

## 1. Objective

Prepare and validate OpenStreetMap (OSM) infrastructure data for the FloodLens AI flood-impact mapping pipeline.

## 2. Data Sources

OpenStreetMap provides the current road and building features used in this preprocessing stage.

Attribution: © OpenStreetMap contributors.

Important limitation: Current OSM features may not represent the infrastructure that existed before the flood. Historical validity must be assessed before final impact estimates are reported.

## 3. Infrastructure Data Prepared

### Roads
- Source features inspected: 44,571
- Geometry type: LineString
- Coordinate reference system: EPSG:4326
- Empty geometries: 0
- Missing geometries: 0

### Buildings
- Source features inspected: 520,315
- Geometry type: Polygon
- Coordinate reference system: EPSG:4326
- Empty geometries: 0
- Missing geometries: 0

## 4. Provisional Study-Area Statistics

The current working boundary is a provisional rectangular area around Betrawati–Gerkhu.

- Approximate area: 545.29 km²
- Road features intersecting the area: 6,004
- Road length within the area: 2,621.165 km
- Building features intersecting the area: 77,932

These are preliminary infrastructure statistics. The team must confirm the final study-area boundary before they are presented as final hackathon results.

## 5. Validation Performed

- Inspected road and building geometry types.
- Checked for missing and empty geometries.
- Recalculated clipped road lengths.
- Confirmed that the saved road-length result matches the recalculated value.
- Recorded source metadata and data-quality limitations.

Pyogrio reported repeated source feature IDs while reading the data. These warnings were recorded; the features have not been removed solely because of repeated IDs.

## 6. Outstanding Work

1. Confirm and validate the team's final study-area boundary.
2. Review OSM infrastructure completeness and historical validity.
3. Obtain additional infrastructure layers, including bridges, health facilities and settlements, if required and available.
4. Preprocess and inspect the pre-flood and post-flood satellite imagery supplied by the satellite-data team member.
5. Validate flood extent and affected-asset calculations before reporting impact estimates.
6. Update the final results and documentation after validation.

Additional OSM queries for bridges, health facilities, schools and settlements timed out. These layers have not yet been collected successfully.

## 7. Limitations

- The current working boundary remains provisional.
- OSM data may not represent pre-flood conditions.
- No validated satellite-derived flood extent is available at this stage.
- Flood damage and road-isolation estimates are not yet validated.
- Missing additional infrastructure layers limit the current analysis.

## 8. Output Files

- `outputs/infrastructure_baseline.json`
- `outputs/provisional_area_baseline.json`
- `outputs/P1_progress_report.md`

## 9. Conclusion

The initial OSM road and building preprocessing and basic geometry checks are complete. The next phase depends on confirming the final study-area boundary, addressing data limitations, and integrating validated satellite-derived flood information.
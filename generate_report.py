import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\FloodLens-P1")
OUTPUT = BASE / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

def read_json(filename):
    path = OUTPUT / filename

    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


baseline = read_json("infrastructure_baseline.json")
area_baseline = read_json("provisional_area_baseline.json")

report = f"""
# FloodLens AI — P1 Data & Preprocessing Report

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 1. Project overview

FloodLens AI is a flood-impact analysis prototype intended to combine
satellite observations with mapped infrastructure.

## 2. Data preparation completed

- OpenStreetMap road and building features were collected.
- Road geometries were filtered into a road-line dataset.
- Building geometries were filtered into a building-polygon dataset.
- An infrastructure baseline summary was generated.
- A provisional study-area baseline was generated.

## 3. Processed datasets

- `data/processed/roads_lines.geojson`
- `data/processed/buildings_polygons.geojson`
- `outputs/infrastructure_baseline.json`
- `outputs/provisional_area_baseline.json`

## 4. Infrastructure baseline
"""

if baseline:
    report += "\n### Overall processed data\n"

    for name, details in baseline.items():
        if isinstance(details, dict):
            report += f"\n#### {name}\n"

            for key, value in details.items():
                report += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        else:
            report += f"\n- **{name}:** {details}\n"
else:
    report += "\nBaseline JSON not found.\n"

if area_baseline:
    report += "\n## 5. Provisional study-area statistics\n\n"
    report += "```json\n"
    report += json.dumps(area_baseline, indent=2)
    report += "\n```\n"

report += """
## 6. Pending work

- Verify the event date and geographic study area.
- Obtain suitable pre-event and post-event satellite imagery.
- Apply an appropriate flood-detection method.
- Compare the resulting flood extent with roads and buildings.
- Validate results and document uncertainty.

## 7. Limitations

No satellite imagery has yet been processed by this pipeline.
Therefore, no flood extent or damaged-infrastructure count is claimed.

The OpenStreetMap data may not represent infrastructure as it existed
before the flood. The study area remains provisional, and road-length
statistics require clipping to the study boundary before being reported
as lengths within that boundary.

## 8. Attribution

© OpenStreetMap contributors.

Satellite-data attribution and training-dataset citations must be added
when the corresponding data sources are selected and used.
"""

report_path = OUTPUT / "P1_progress_report.md"
report_path.write_text(report, encoding="utf-8")

print("=" * 55)
print("FLOODLENS AI - P1 REPORT GENERATED")
print("=" * 55)
print(f"Report: {report_path}")
print("\nThis is a progress report, not a completed flood-detection report.")
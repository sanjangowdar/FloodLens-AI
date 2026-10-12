# FloodLens AI - P1 Data & Preprocessing

## Overview
FloodLens AI is a prototype for flood-impact assessment that aims to
combine satellite observations with geospatial infrastructure data.

P1 is responsible for collecting, checking, and preparing the
infrastructure datasets for downstream analysis.

## Technology Stack
- Python
- GeoPandas
- OSMnx
- Shapely
- Rasterio
- NumPy
- Matplotlib

## Project Structure
```text
FloodLens-P1/
├── data/
│   ├── osm/
│   └── processed/
├── outputs/
├── get_map_data.py
├── check_data.py
├── prepare_data.py
├── analyze_data.py
├── check_area.py
├── clip_infrastructure.py
├── detect_flood.py
├── estimate_impact.py
├── generate_report.py
├── requirements.txt
└── README.md
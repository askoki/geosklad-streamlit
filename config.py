"""Application configuration for the Vransko jezero viewer."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
LAKE_GEOJSON = DATA_DIR / "vransko_lake.geojson"
META_JSON = DATA_DIR / "vransko_meta.json"

START_DATE = "2025-01-01"
END_DATE = "2026-01-01"
DEFAULT_PAD_M = 500

SENSOR_LABELS = {
    "S2": "Sentinel-2",
    "L8": "Landsat 8",
    "L9": "Landsat 9",
}

INDICES = {
    "NDVI": {
        "bands": ("nir", "red"),
        "vis": {"min": -0.2, "max": 0.8, "palette": ["#a50026", "#ffffbf", "#006837"]},
        "label": "Vegetation",
    },
    "NDWI": {
        "bands": ("green", "nir"),
        "vis": {"min": -0.3, "max": 0.6, "palette": ["#8c510a", "#f6e8c3", "#c7eae5", "#2166ac"]},
        "label": "Water",
    },
    "NDCI": {
        "bands": ("rededge1", "red"),
        "vis": {"min": -0.1, "max": 0.3, "palette": ["#2c7bb6", "#abd9e9", "#ffffbf", "#fdae61", "#d7191c"]},
        "label": "Chlorophyll",
    },
    "NDTI": {
        "bands": ("red", "green"),
        "vis": {"min": -0.2, "max": 0.2, "palette": ["#053061", "#4393c3", "#f7f7f7", "#d6604d", "#67001f"]},
        "label": "Turbidity",
    },
}

TRUE_COLOR_VIS = {"min": 0, "max": 0.3, "bands": ["red", "green", "blue"]}

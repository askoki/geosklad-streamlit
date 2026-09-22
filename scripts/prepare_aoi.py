#!/usr/bin/env python3
"""Polygonize and simplify the August 2025 shoreline shapefile."""

import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import mapping
from shapely.ops import polygonize, unary_union

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "source" / "granica_Vransko.shp"
OUTPUT = ROOT / "data" / "vransko_lake.geojson"
META = ROOT / "data" / "vransko_meta.json"


def main():
    source = gpd.read_file(SOURCE)
    assert source.crs is not None and source.crs.to_epsg() == 32633, source.crs

    lines = list(source.geometry.explode(index_parts=False))
    polygons = list(polygonize(lines))
    assert len(polygons) == 1, f"Expected one polygon, found {len(polygons)}"
    polygon = unary_union(polygons)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)
    assert polygon.is_valid and polygon.geom_type == "Polygon"
    area_km2 = polygon.area / 1e6
    assert 28.9 <= area_km2 <= 29.1, area_km2

    source_bounds = [round(float(value)) for value in polygon.bounds]
    simplified = polygon.simplify(10, preserve_topology=True)
    assert simplified.is_valid
    area_change_pct = abs(simplified.area - polygon.area) / polygon.area * 100

    wgs84 = gpd.GeoSeries([simplified], crs="EPSG:32633").to_crs("EPSG:4326").iloc[0]
    feature_collection = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Vransko jezero shoreline", "source_date": "2025-08-26"},
                "geometry": mapping(wgs84),
            }
        ],
    }
    OUTPUT.write_text(json.dumps(feature_collection, separators=(",", ":")), encoding="utf-8")
    META.write_text(
        json.dumps(
            {
                "crs": "EPSG:32633",
                "bounds_utm": source_bounds,
                "area_km2": round(area_km2, 2),
                "source_date": "2025-08-26",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    roundtrip = gpd.GeoSeries.from_file(OUTPUT).to_crs("EPSG:32633").iloc[0]
    assert roundtrip.is_valid
    assert 28.9 <= roundtrip.area / 1e6 <= 29.1
    assert all(abs(a - b) < 1 for a, b in zip(roundtrip.bounds, simplified.bounds))
    print(f"Wrote {OUTPUT.relative_to(ROOT)}: {area_km2:.2f} km², {len(wgs84.exterior.coords)} vertices")
    print(f"Simplification area change: {area_change_pct:.4f}%")
    print(f"UTM bounds: {source_bounds}")


if __name__ == "__main__":
    main()

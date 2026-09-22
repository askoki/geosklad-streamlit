"""Runtime AOI construction without geopandas."""

import json

import ee

from config import LAKE_GEOJSON, META_JSON


def _geometry_from_geojson(payload):
    """Accept a FeatureCollection, Feature, or bare GeoJSON geometry."""
    if payload.get("type") == "FeatureCollection":
        return payload["features"][0]["geometry"]
    if payload.get("type") == "Feature":
        return payload["geometry"]
    return payload


def lake_geom():
    with LAKE_GEOJSON.open(encoding="utf-8") as handle:
        return ee.Geometry(_geometry_from_geojson(json.load(handle)))


def bbox_geom(pad_m=500):
    with META_JSON.open(encoding="utf-8") as handle:
        x0, y0, x1, y1 = json.load(handle)["bounds_utm"]
    pad = float(pad_m)
    return ee.Geometry.Rectangle(
        [x0 - pad, y0 - pad, x1 + pad, y1 + pad],
        proj="EPSG:32633",
        geodesic=False,
    )


def aoi_geom(extent, pad_m=500):
    if extent == "lake":
        return lake_geom()
    if extent == "bbox":
        return bbox_geom(pad_m)
    raise ValueError(f"Unknown AOI extent: {extent!r}")

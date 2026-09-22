"""All Streamlit cache boundaries and EE round trips."""

import math
import os

import ee
import requests
import streamlit as st

import aoi as aoi_module
import catalog
import gee
from config import INDICES, TRUE_COLOR_VIS


def _visualized_scene(asset_id, sensor, extent, pad_m, index, water_mask, vmin, vmax):
    image = gee.load_scene(asset_id, sensor, aoi(extent, pad_m))
    if index == "true_color":
        return gee.true_color(image).visualize(**TRUE_COLOR_VIS)
    vis = dict(INDICES[index]["vis"], min=float(vmin), max=float(vmax))
    return gee.normalized_index(image, index, water_mask).visualize(**vis)


@st.cache_resource(show_spinner="Connecting to Earth Engine…")
def init_ee():
    # Prefer a [gee_service_account] TOML table. It avoids the private_key
    # newline JSONDecodeError common with a single pasted JSON string.
    try:
        secret_values = st.secrets.to_dict()
    except Exception:  # No secrets file is valid for locally authenticated EE.
        secret_values = {}
    service_account = secret_values.get("gee_service_account") or os.environ.get(
        "GEE_SERVICE_ACCOUNT_JSON"
    )
    gee.init_ee(
        project=secret_values.get("GEE_PROJECT")
        or os.environ.get("GEE_PROJECT", "utomika"),
        service_account_json=service_account,
    )
    return True


@st.cache_resource(show_spinner=False)
def aoi(extent, pad_m):
    return aoi_module.aoi_geom(extent, pad_m)


@st.cache_data(show_spinner=False)
def aoi_view(extent, pad_m):
    selected = aoi(extent, pad_m)
    lake = aoi_module.lake_geom()
    lon, lat = selected.centroid(maxError=1).coordinates().getInfo()
    # Leaflet/Folium expects GeoJSON coordinates in WGS84. The bbox is built in
    # EPSG:32633 so its padding is measured in metres; transform only the
    # browser-facing geometry while keeping Earth Engine analysis in UTM.
    bbox = (
        selected.transform("EPSG:4326", maxError=1).getInfo()
        if extent == "bbox"
        else None
    )
    return {
        "center": [lat, lon],
        "lake": lake.getInfo(),
        "bbox": bbox,
        "area_km2": selected.area(maxError=1).divide(1e6).getInfo(),
    }


@st.cache_data(ttl=3600, show_spinner="Loading 2025 scenes…")
def scenes(extent, pad_m):
    return catalog.list_scenes(aoi(extent, pad_m))


@st.cache_data(ttl=1800, show_spinner=False)
def index_tile(asset_id, sensor, extent, pad_m, index, water_mask, vmin, vmax):
    visualized = _visualized_scene(
        asset_id, sensor, extent, pad_m, index, water_mask, vmin, vmax
    )
    return gee.tile_layer_url(visualized, {})


@st.cache_data(ttl=1800, show_spinner=False)
def index_png(asset_id, sensor, extent, pad_m, index, water_mask, vmin, vmax):
    """Return a 2048 px display-rendered PNG for the selected AOI and layer."""
    geom = aoi(extent, pad_m)
    visualized = _visualized_scene(
        asset_id, sensor, extent, pad_m, index, water_mask, vmin, vmax
    )
    url = visualized.getThumbURL(
        {"region": geom, "dimensions": 2048, "format": "png"}
    )
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    if not response.content.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("Earth Engine did not return a PNG image")
    return response.content


@st.cache_data(ttl=1800, show_spinner="Calculating AOI statistics…")
def scene_stats(asset_id, sensor, extent, pad_m):
    geom = aoi(extent, pad_m)
    image = gee.load_scene(asset_id, sensor, geom)
    quality = gee.scene_quality(asset_id, sensor, geom).getInfo()
    valid = quality.get("valid") or 0.0
    cloud = quality.get("cloud") or 0.0

    indices = []
    for name in gee.available_indices(sensor):
        indices.append(gee.normalized_index(image, name, name in {"NDCI", "NDTI"}))
    stack = ee.Image.cat(indices)
    means = stack.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geom,
        crs="EPSG:32633",
        scale=gee.SENSORS[sensor]["native_m"],
        maxPixels=1e9,
        bestEffort=True,
    ).getInfo()
    return {
        "aoi_cloud_pct": (cloud / valid * 100) if valid else math.nan,
        "means": means,
    }

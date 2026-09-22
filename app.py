"""Vransko jezero 2025 water-index viewer."""

import math

import streamlit as st

import resources
from components.legend import render_legends
from components.map_view import render_map
from components.sidebar import render_sidebar
from config import SENSOR_LABELS

st.set_page_config(page_title="Vransko jezero indices", page_icon="🌊", layout="wide")

st.title("Vransko jezero · 2025")
st.caption("Explore vegetation, water, chlorophyll, and turbidity indicators from Sentinel-2 and Landsat 8/9.")

try:
    resources.init_ee()
    controls = render_sidebar()
except Exception as error:
    st.error(f"Earth Engine could not be initialized: {error}")
    st.info("Configure .streamlit/secrets.toml or authenticate Earth Engine locally, then reload.")
    st.stop()

if controls is None:
    st.stop()

scene = controls["scene"]
asset_id = scene["asset_id"]
sensor = scene["sensor"]
extent = controls["extent"]
pad_m = controls["pad_m"]

st.subheader(f"{scene['date'].isoformat()} · {SENSOR_LABELS[sensor]}")
view = resources.aoi_view(extent, pad_m)
stats = resources.scene_stats(asset_id, sensor, extent, pad_m)

scene_cloud = scene["scene_cloud_pct"]
aoi_cloud = stats["aoi_cloud_pct"]
metrics = st.columns(4)
metrics[0].metric("Sensor", sensor)
metrics[1].metric("Scene cloud", "n/a" if scene_cloud != scene_cloud else f"{scene_cloud:.1f}%")
metrics[2].metric("AOI cloud", "n/a" if math.isnan(aoi_cloud) else f"{aoi_cloud:.1f}%")
metrics[3].metric("AOI area", f"{view['area_km2']:.1f} km²")

with st.spinner("Preparing map layers…"):
    tiles = {
        "True colour": resources.index_tile(
            asset_id, sensor, extent, pad_m, "true_color", False, 0, 0.3
        )
    }
    for index_name in controls["active_indices"]:
        vmin, vmax = controls["ranges"][index_name]
        tiles[index_name] = resources.index_tile(
            asset_id,
            sensor,
            extent,
            pad_m,
            index_name,
            controls["water_mask"],
            vmin,
            vmax,
        )

render_map(view, tiles, asset_id.rsplit("/", 1)[-1])
render_legends(controls["active_indices"], controls["ranges"])

with st.expander("Methods and selected-scene means"):
    st.markdown(
        "All indices use cloud-masked surface reflectance. NDCI and NDTI are restricted "
        "to pixels with NDWI > 0 when **Water only** is enabled. NDCI is only available "
        "for Sentinel-2 because Landsat 8/9 has no red-edge band. See `METHODS.md` for details."
    )
    available_means = {
        name: round(value, 3)
        for name, value in stats["means"].items()
        if value is not None
    }
    st.json(available_means)

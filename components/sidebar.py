"""Sidebar controls and scene selection."""

import calendar
import datetime as dt

import streamlit as st

import gee
import resources
from config import DEFAULT_PAD_M, INDICES, SENSOR_LABELS


def _scene_label(row):
    cloud = row["scene_cloud_pct"]
    cloud_text = "n/a" if cloud != cloud else f"{cloud:.0f}%"
    return f"{row['date'].isoformat()} · {row['sensor']} · cloud {cloud_text}"


def render_sidebar():
    with st.sidebar:
        st.header("View")
        extent_label = st.radio(
            "AOI extent",
            ["Lake (shoreline, 28.98 km²)", "Surrounding area (bbox)"],
        )
        extent = "lake" if extent_label.startswith("Lake") else "bbox"
        pad_m = (
            st.slider("Bounding-box padding (m)", 0, 2000, DEFAULT_PAD_M, 250)
            if extent == "bbox"
            else DEFAULT_PAD_M
        )
        sensors = st.multiselect(
            "Sensors",
            list(SENSOR_LABELS),
            default=list(SENSOR_LABELS),
            format_func=lambda value: SENSOR_LABELS[value],
        )
        max_cloud = st.slider("Max scene cloud %", 0, 100, 100)
        months = st.multiselect(
            "Months",
            list(range(1, 13)),
            default=list(range(1, 13)),
            format_func=lambda value: calendar.month_abbr[value],
        )
        water_mask = st.checkbox("Water only (NDWI > 0) for NDCI/NDTI", value=True)

        frame = resources.scenes(extent, pad_m)
        filtered = frame[
            frame["sensor"].isin(sensors)
            & frame["date"].map(lambda value: value.month in months)
            & (frame["scene_cloud_pct"].fillna(100) <= max_cloud)
        ].reset_index(drop=True)
        if filtered.empty:
            st.warning("No scenes match these filters.")
            return None

        target = dt.date(2025, 8, 26)
        default_index = min(
            range(len(filtered)), key=lambda i: abs((filtered.iloc[i]["date"] - target).days)
        )
        selected_index = st.radio(
            f"Scene ({len(filtered)} found)",
            range(len(filtered)),
            index=default_index,
            format_func=lambda i: _scene_label(filtered.iloc[i]),
        )
        scene = filtered.iloc[selected_index].to_dict()

        available = gee.available_indices(scene["sensor"])
        active_indices = st.multiselect(
            "Map indices",
            available,
            default=available,
            format_func=lambda name: f"{name} — {INDICES[name]['label']}",
        )
        ranges = {}
        with st.expander("Display ranges"):
            for name in available:
                defaults = INDICES[name]["vis"]
                ranges[name] = st.slider(
                    name,
                    -1.0,
                    1.0,
                    (float(defaults["min"]), float(defaults["max"])),
                    0.01,
                )

    return {
        "extent": extent,
        "pad_m": pad_m,
        "scene": scene,
        "active_indices": active_indices,
        "water_mask": water_mask,
        "ranges": ranges,
    }

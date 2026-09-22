"""Folium map rendering."""

import folium
import streamlit as st
from streamlit_folium import st_folium


def render_map(view, tiles, scene_id):
    m = folium.Map(
        location=view["center"], zoom_start=11, tiles=None, control_scale=True
    )
    folium.TileLayer(
        "CartoDB positron", control=False, cross_origin=True
    ).add_to(m)

    for name, url in tiles.items():
        folium.TileLayer(
            tiles=url,
            attr="Google Earth Engine",
            name=name,
            overlay=True,
            control=True,
            show=name == "True colour",
            cross_origin=True,
        ).add_to(m)

    folium.GeoJson(
        view["lake"],
        name="August 2025 shoreline",
        style_function=lambda _feature: {
            "color": "yellow",
            "weight": 3,
            "fill": False,
        },
    ).add_to(m)
    if view["bbox"] is not None:
        folium.GeoJson(
            view["bbox"],
            name="Analysis extent",
            style_function=lambda _feature: {
                "color": "white",
                "weight": 2,
                "dashArray": "7 5",
                "fill": False,
            },
        ).add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    # Force a fresh Leaflet instance whenever visualization parameters change.
    # Otherwise the component can preserve stale client-side tile URLs.
    tile_signature = abs(hash(tuple(tiles.items())))
    st_folium(
        m,
        height=600,
        use_container_width=True,
        returned_objects=[],
        key=f"map_{scene_id}_{'bbox' if view['bbox'] else 'lake'}_{tile_signature}",
    )

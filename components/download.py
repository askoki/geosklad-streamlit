"""On-demand PNG preparation for the selected scene and AOI."""

import streamlit as st

import resources
from config import INDICES


def _filename(scene, layer, extent, pad_m):
    area = "lake" if extent == "lake" else f"bbox_{pad_m}m"
    return (
        f"vransko_{scene['date'].isoformat()}_{scene['sensor']}_"
        f"{layer.lower()}_{area}.png"
    )


def render_download(scene, controls):
    """Render a single-layer, current-AOI PNG download workflow."""
    layers = ["true_color", *controls["ranges"]]
    labels = {"true_color": "True colour", **{name: name for name in INDICES}}

    with st.expander("Download image"):
        st.caption(
            "Prepare a display-ready PNG clipped to the selected lake or bounding-box "
            "extent. The PNG uses the current palette, range, cloud mask, and water-mask "
            "setting; basemap and boundary outlines are not embedded."
        )
        layer = st.selectbox(
            "Layer",
            layers,
            format_func=lambda value: labels[value],
            key="download_layer",
        )
        if layer == "true_color":
            vmin, vmax = 0.0, 0.3
            water_mask = False
        else:
            vmin, vmax = controls["ranges"][layer]
            water_mask = controls["water_mask"]

        signature = (
            scene["asset_id"],
            scene["sensor"],
            controls["extent"],
            controls["pad_m"],
            layer,
            water_mask,
            vmin,
            vmax,
        )
        if st.button("Prepare PNG", type="primary"):
            with st.spinner("Rendering the download…"):
                payload = resources.index_png(*signature)
            st.session_state["_prepared_png"] = {
                "signature": signature,
                "payload": payload,
            }

        prepared = st.session_state.get("_prepared_png")
        if prepared and prepared["signature"] == signature:
            st.download_button(
                "Download PNG",
                data=prepared["payload"],
                file_name=_filename(
                    scene, layer, controls["extent"], controls["pad_m"]
                ),
                mime="image/png",
            )

"""Compact CSS colorbars shown below the map."""

import html

import streamlit as st

from config import INDICES


def render_legends(active_indices, ranges):
    if not active_indices:
        return
    blocks = []
    for name in active_indices:
        vmin, vmax = ranges[name]
        midpoint = (vmin + vmax) / 2
        palette = ", ".join(INDICES[name]["vis"]["palette"])
        blocks.append(
            f'<div class="index-legend">'
            f'<div class="legend-title">{html.escape(name)} · {html.escape(INDICES[name]["label"])}</div>'
            f'<div class="legend-bar" style="background:linear-gradient(to right,{palette})"></div>'
            f'<div class="legend-values"><span>{vmin:.2f}</span><span>{midpoint:.2f}</span><span>{vmax:.2f}</span></div>'
            "</div>"
        )
    st.markdown(
        """
        <style>
        .legends {display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1rem;margin:.25rem 0 1rem}
        .legend-title {font-size:.85rem;font-weight:600;margin-bottom:.3rem}
        .legend-bar {height:12px;border-radius:3px;border:1px solid rgba(0,0,0,.18)}
        .legend-values {display:flex;justify-content:space-between;font-size:.75rem;color:#555;margin-top:.15rem}
        </style>
        <div class="legends">"""
        + "".join(blocks)
        + "</div>",
        unsafe_allow_html=True,
    )

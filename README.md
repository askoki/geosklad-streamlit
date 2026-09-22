# geosklad-streamlit

An interactive Streamlit viewer for NDVI, NDWI, NDCI, and NDTI at Vransko jezero during 2025. It queries live Google Earth Engine catalogs for Sentinel-2 and Landsat 8/9, and includes both the minimum-water shoreline measured on 2025-08-26 and a padded surrounding extent.

## Setup

Python 3.10+ and an Earth Engine-enabled Google Cloud project are required.

```bash
uv venv
uv pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Fill `.streamlit/secrets.toml` with `GEE_PROJECT` and the service-account table. Alternatively, omit the service-account table after authenticating Earth Engine locally.

Set the viewer password through the environment. The app fails closed when this variable is missing:

```bash
export APP_PASSWORD="choose-a-strong-password"
```

## Rebuild the shoreline data

The source shapefile is included under `data/source/`. Geospatial libraries are only required for this one-off derivation, not by the application:

```bash
uv run --with geopandas scripts/prepare_aoi.py
```

## Verify Earth Engine

Run the isolated catalog smoke test before starting the UI:

```bash
python scripts/check_gee.py
```

## Run

```bash
streamlit run app.py
```

Choose the lake shoreline or surrounding bounding box, filter the 2025 scenes, then switch map layers with the layer control. NDCI appears only for Sentinel-2 scenes.

The interactive map uses Folium/Leaflet without a third-party basemap. It shows
only the Google Earth Engine imagery clipped to the selected lake or analysis
extent, so no map-provider API key is needed. Earth Engine authentication is
still required to query and render those scientific satellite layers; it does
not require a Google Maps API key.

The **Download image** panel prepares a 2048 px PNG of true colour or any index available for the selected sensor. It uses the current AOI, padding, display range, cloud mask, and water-mask setting. The basemap and vector outlines are intentionally omitted from the raster download.

## Deploy

`app.py` exports an ASGI-compatible Streamlit application, while `streamlit_app.py`
contains the UI. This lets Streamlit hosts and Vercel use the same entry point.

For Vercel, deploy the repository root and enable Fluid Compute so Streamlit's
WebSocket connection can stay attached to the Python function. Configure
`APP_PASSWORD`, `GEE_PROJECT`, and `GEE_SERVICE_ACCOUNT_JSON` as environment
variables. The last value is the complete Google service-account JSON document.
Never commit `.streamlit/secrets.toml`, which is ignored by Git.

Scientific assumptions and caveats are documented in [METHODS.md](METHODS.md).

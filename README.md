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

The **Download image** panel prepares a 2048 px PNG of true colour or any index available for the selected sensor. It uses the current AOI, padding, display range, cloud mask, and water-mask setting. The basemap and vector outlines are intentionally omitted from the raster download.

## Deploy

Deploy the repository as a Streamlit app with `app.py` as the entry point. Add the same `GEE_PROJECT` and `[gee_service_account]` values to the host's secrets manager, and configure `APP_PASSWORD` as an environment variable. Never commit `.streamlit/secrets.toml`; it is ignored by Git.

Scientific assumptions and caveats are documented in [METHODS.md](METHODS.md).

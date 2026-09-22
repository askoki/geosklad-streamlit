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

## Deploy

Deploy the repository as a Streamlit app with `app.py` as the entry point. Add the same `GEE_PROJECT` and `[gee_service_account]` values to the host's secrets manager. Never commit `.streamlit/secrets.toml`; it is ignored by Git.

Scientific assumptions and caveats are documented in [METHODS.md](METHODS.md).

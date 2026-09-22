"""Live 2025 Earth Engine scene catalog."""

import pandas as pd
import ee

from config import END_DATE, START_DATE
from gee import SENSORS


def _collection_features(sensor, geom):
    spec = SENSORS[sensor]
    collection_id = spec["collection"]
    collection = (
        ee.ImageCollection(collection_id)
        .filterBounds(geom)
        # The lake straddles neighboring catalog footprints. Require complete
        # AOI coverage so an edge-only granule cannot paint just a sliver.
        .filter(ee.Filter.contains(leftField=".geo", rightValue=geom))
        .filterDate(START_DATE, END_DATE)
    )

    def describe(image):
        return ee.Feature(
            None,
            {
                "date": image.date().format("YYYY-MM-dd"),
                "datetime": image.date().format("YYYY-MM-dd'T'HH:mm:ss'Z'"),
                "sensor": sensor,
                "asset_id": ee.String(collection_id)
                .cat("/")
                .cat(ee.String(image.get("system:index"))),
                "scene_cloud_pct": image.get(spec["cloud_property"]),
            },
        )

    return ee.FeatureCollection(collection.map(describe))


def list_scenes(geom):
    merged = None
    for sensor in SENSORS:
        features = _collection_features(sensor, geom)
        merged = features if merged is None else merged.merge(features)
    payload = merged.sort("datetime", False).getInfo()
    rows = [feature["properties"] for feature in payload.get("features", [])]
    columns = ["date", "datetime", "sensor", "asset_id", "scene_cloud_pct"]
    if not rows:
        return pd.DataFrame(columns=columns)
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"]).dt.date
    frame["datetime"] = pd.to_datetime(frame["datetime"], utc=True)
    frame["scene_cloud_pct"] = pd.to_numeric(frame["scene_cloud_pct"], errors="coerce")
    # Neighboring footprints can both fully cover this small AOI on one pass.
    # Keep the provider-reported clearest asset for each sensor and date.
    frame = frame.sort_values(
        ["date", "sensor", "scene_cloud_pct"], ascending=[False, True, True]
    ).drop_duplicates(["date", "sensor"], keep="first")
    return frame[columns].sort_values("datetime", ascending=False).reset_index(drop=True)

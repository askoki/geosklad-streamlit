"""Google Earth Engine sensor, mask, index, and tile helpers."""

import json

import ee

from config import INDICES, TRUE_COLOR_VIS

SENSORS = {
    "S2": {
        "collection": "COPERNICUS/S2_SR_HARMONIZED",
        "native": ["B2", "B3", "B4", "B5", "B8"],
        "common": ["blue", "green", "red", "rededge1", "nir"],
        "bands": {"blue", "green", "red", "rededge1", "nir"},
        "quality": ["SCL"],
        "scale": 1e-4,
        "offset": 0.0,
        "native_m": 20,
        "cloud_property": "CLOUDY_PIXEL_PERCENTAGE",
    },
    "L8": {
        "collection": "LANDSAT/LC08/C02/T1_L2",
        "native": ["SR_B2", "SR_B3", "SR_B4", "SR_B5"],
        "common": ["blue", "green", "red", "nir"],
        "bands": {"blue", "green", "red", "nir"},
        "quality": ["QA_PIXEL", "QA_RADSAT"],
        "scale": 2.75e-5,
        "offset": -0.2,
        "native_m": 30,
        "cloud_property": "CLOUD_COVER",
    },
    "L9": {
        "collection": "LANDSAT/LC09/C02/T1_L2",
        "native": ["SR_B2", "SR_B3", "SR_B4", "SR_B5"],
        "common": ["blue", "green", "red", "nir"],
        "bands": {"blue", "green", "red", "nir"},
        "quality": ["QA_PIXEL", "QA_RADSAT"],
        "scale": 2.75e-5,
        "offset": -0.2,
        "native_m": 30,
        "cloud_property": "CLOUD_COVER",
    },
}


def init_ee(project="utomika", service_account_json=None):
    """Initialize EE with a service-account table or local credentials."""
    if service_account_json:
        info = (
            json.loads(service_account_json)
            if isinstance(service_account_json, str)
            else dict(service_account_json)
        )
        credentials = ee.ServiceAccountCredentials(
            info["client_email"], key_data=json.dumps(info)
        )
        ee.Initialize(credentials, project=project)
    else:
        ee.Initialize(project=project)


def available_indices(sensor):
    supplied = SENSORS[sensor]["bands"]
    return [name for name, spec in INDICES.items() if set(spec["bands"]) <= supplied]


def _quality(image, sensor):
    """Return (valid-source mask, cloudy-or-saturated mask)."""
    if sensor == "S2":
        scl = image.select("SCL")
        valid = scl.mask().And(scl.neq(0))
        cloudy = (
            scl.eq(1)
            .Or(scl.eq(3))
            .Or(scl.eq(8))
            .Or(scl.eq(9))
            .Or(scl.eq(10))
        )
        return valid, cloudy.And(valid)

    qa = image.select("QA_PIXEL")
    valid = qa.mask().And(qa.bitwiseAnd(1).eq(0))
    bits = (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)
    cloudy = qa.bitwiseAnd(bits).neq(0).Or(image.select("QA_RADSAT").neq(0))
    return valid, cloudy.And(valid)


def load_scene(asset_id, sensor, geom=None):
    """Load, harmonize, scale, strictly cloud-mask, and optionally clip a scene."""
    spec = SENSORS[sensor]
    raw = ee.Image(asset_id)
    valid, cloudy = _quality(raw, sensor)
    clean = valid.And(cloudy.Not())
    image = (
        raw.select(spec["native"], spec["common"])
        .multiply(spec["scale"])
        .add(spec["offset"])
        .updateMask(clean)
    )
    return image.clip(geom) if geom is not None else image


def normalized_index(image, index_name, water_mask=False):
    """Calculate a guarded normalized-difference index on scaled reflectance."""
    if index_name not in INDICES:
        raise ValueError(f"Unknown index: {index_name}")
    first_name, second_name = INDICES[index_name]["bands"]
    first = image.select(first_name)
    second = image.select(second_name)
    denominator = first.add(second)
    result = (
        first.subtract(second)
        .divide(denominator)
        .updateMask(denominator.abs().gt(1e-12))
        .rename(index_name)
    )
    if water_mask and index_name in {"NDCI", "NDTI"}:
        ndwi = normalized_index(image, "NDWI")
        result = result.updateMask(ndwi.gt(0))
    return result


def true_color(image):
    return image.select(TRUE_COLOR_VIS["bands"])


def scene_quality(asset_id, sensor, geom):
    raw = ee.Image(asset_id)
    valid, cloudy = _quality(raw, sensor)
    values = (
        valid.rename("valid")
        .unmask(0, False)
        .addBands(cloudy.rename("cloud").unmask(0, False))
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geom,
            crs="EPSG:32633",
            scale=SENSORS[sensor]["native_m"],
            maxPixels=1e9,
            bestEffort=True,
        )
    )
    return values


def tile_layer_url(image, vis):
    return image.getMapId(vis)["tile_fetcher"].url_format

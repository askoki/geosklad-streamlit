# Methods

## Area of interest

The yellow outline is the shoreline observed on 2025-08-26, when the lake was at its 2025 minimum. The supplied closed line was polygonized in EPSG:32633, simplified by 10 m while preserving topology, and then converted to WGS84. It encloses 28.98 km². The surrounding-area option uses its UTM bounding box plus an exact metre-based padding.

Earlier 2025 scenes can show water outside the fixed polygon. This is expected and is the reason the surrounding bounding-box view is available.

## Reflectance and indices

Sentinel-2 uses `COPERNICUS/S2_SR_HARMONIZED` with a 0.0001 scale. Landsat 8/9 Collection 2 Level 2 uses a 0.0000275 scale and −0.2 offset. Every index is calculated from scaled surface reflectance with a guarded denominator.

| Index | Sentinel-2 | Landsat 8/9 | Interpretation |
|---|---|---|---|
| NDVI | `(B8 − B4) / (B8 + B4)` | `(SR_B5 − SR_B4) / (SR_B5 + SR_B4)` | vegetation |
| NDWI | `(B3 − B8) / (B3 + B8)` | `(SR_B3 − SR_B5) / (SR_B3 + SR_B5)` | open water |
| NDCI | `(B5 − B4) / (B5 + B4)` | unavailable | relative chlorophyll indicator |
| NDTI | `(B4 − B3) / (B4 + B3)` | `(SR_B4 − SR_B3) / (SR_B4 + SR_B3)` | relative turbidity indicator |

NDCI is unavailable on Landsat 8/9 because OLI has no red-edge band. Landsat B5 is near infrared, not the Sentinel-2 B5 red-edge equivalent.

When **Water only (NDWI > 0)** is enabled, the selected scene's NDCI and NDTI pixels are additionally masked to NDWI > 0. NDVI and NDWI are never water-masked.

## Cloud masking

Sentinel-2 excludes Scene Classification Layer values 0 (no data), 1 (saturated/defective), 3 (cloud shadow), 8 (medium-probability cloud), 9 (high-probability cloud), and 10 (cirrus). Water (6) and snow/ice (11) remain eligible.

Landsat excludes `QA_PIXEL` bit 1 (dilated cloud), bit 2 (cirrus), bit 3 (cloud), and bit 4 (cloud shadow), as well as every pixel with nonzero `QA_RADSAT`. The catalog filter uses the provider's scene-wide cloud percentage. AOI cloud percentage is calculated lazily only for the selected scene.

Because the lake straddles neighboring satellite catalog footprints, the catalog requires a scene to cover the full AOI. This removes edge-only granules that would otherwise render only a narrow sliver. When neighboring footprints both cover the AOI on the same sensor/date, the catalog keeps the one with the lower provider-reported cloud percentage.

## Resolution

Statistics use EPSG:32633 at 20 m for Sentinel-2, avoiding artificial upsampling of its 20 m red-edge band, and 30 m for Landsat 8/9.

## Interpretation caveats

Landsat Collection 2 Level 2 surface reflectance is atmospherically corrected for land. Its absolute values over water are unreliable. NDTI and NDWI trends within Landsat scenes can be useful, but absolute values should not be compared directly with Sentinel-2.

Sentinel-2 L2A (Sen2Cor) is also a land-oriented atmospheric correction. For rigorous chlorophyll analysis, use an aquatic processor such as ACOLITE or C2RCC. NDCI in this viewer is a relative indicator, not a chlorophyll concentration measurement.

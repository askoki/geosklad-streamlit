#!/usr/bin/env python3
"""Authenticate and print 2025 scene counts for both AOI extents."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import aoi  # noqa: E402
import catalog  # noqa: E402
import gee  # noqa: E402


def main():
    gee.init_ee()
    for extent, pad in (("lake", 500), ("bbox", 500)):
        geom = aoi.aoi_geom(extent, pad)
        frame = catalog.list_scenes(geom)
        values = frame.groupby("sensor").size().to_dict()
        print(f"{extent} (pad={pad} m): " + ", ".join(f"{key}={value}" for key, value in values.items()))


if __name__ == "__main__":
    main()

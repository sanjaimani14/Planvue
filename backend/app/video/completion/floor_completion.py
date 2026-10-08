"""
Floor Completion Module for Mode B.
Ensures the ground floor slab is a continuous planar manifold bounded by wall footprints.
"""
from typing import List, Dict, Any, Tuple
import math
import numpy as np

from backend.app.video.schemas import CompletionRegion, PlaneSurface

def complete_floor_slab(
    wall_boundaries: List[Dict[str, Any]],
    floor_elevation_y: float = 0.0,
    thickness: float = 0.15
) -> Dict[str, Any]:
    """
    Constructs a solid floor slab geometry enclosing the room boundary perimeter.
    """
    if not wall_boundaries:
        # Fallback default room box
        return {
            "id": "floor_slab_completed",
            "type": "floor",
            "status": "INFERRED",
            "bounds": {"min": [-3.0, floor_elevation_y - thickness, -3.0], "max": [3.0, floor_elevation_y, 3.0]},
            "thickness": thickness,
            "elevation": floor_elevation_y,
            "area_m2": 36.0
        }

    # Extract polygon footprint bounds from wall endpoints
    xs = []
    zs = []
    for w in wall_boundaries:
        st = w.get("start", [0, 0, 0])
        en = w.get("end", [0, 0, 0])
        xs.extend([st[0], en[0]])
        zs.extend([st[2], en[2]])

    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    area = round(abs(max_x - min_x) * abs(max_z - min_z), 2)

    return {
        "id": "floor_slab_completed",
        "type": "floor",
        "status": "INFERRED",
        "bounds": {
            "min": [round(min_x, 2), round(floor_elevation_y - thickness, 2), round(min_z, 2)],
            "max": [round(max_x, 2), round(floor_elevation_y, 2), round(max_z, 2)]
        },
        "thickness": thickness,
        "elevation": floor_elevation_y,
        "area_m2": area
    }

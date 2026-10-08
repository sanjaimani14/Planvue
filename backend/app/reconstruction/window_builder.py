import math
import numpy as np
import trimesh
from typing import List, Dict, Any, Tuple, Optional

COLOR_WINDOW_FRAME = [71, 85, 105, 255]     # Dark architectural slate
COLOR_WINDOW_GLASS = [147, 197, 253, 180]    # Light cyan/blue translucent glass

def build_window_geometry(
    window: Dict[str, Any],
    wall_map: Dict[str, Dict[str, Any]],
    default_height: float = 1.20,
    default_width: float = 1.20,
    default_sill_height: float = 0.90,
    origin_offset: Tuple[float, float] = (0.0, 0.0)
) -> Dict[str, Any]:
    """
    Constructs 3D window frame and glazing pane:
    - Associates window with parent wall orientation and position
    - Default height: 1.2m, sill height: 0.9m (center at sill_height + height / 2 = 1.5m)
    - If wall association is missing, flags as unresolved
    """
    wall_id = window.get("wall_id")
    parent_wall = wall_map.get(wall_id) if wall_id else None

    # Determine metric coordinates
    mp = window.get("metric_position")
    if mp:
        wx = mp[0] - origin_offset[0]
        wz = mp[1] - origin_offset[1]
    else:
        scale = 0.02
        pos = window.get("position", [0.0, 0.0])
        wx = pos[0] * scale - origin_offset[0]
        wz = pos[1] * scale - origin_offset[1]

    width_m = float(window.get("width_m") or default_width)
    height_m = float(window.get("height_m") or default_height)
    sill_height_m = float(window.get("sill_height_m") or default_sill_height)
    status = window.get("status", "OBSERVED")
    confidence = float(window.get("confidence") or 0.85)

    yaw = 0.0
    is_resolved = True

    if parent_wall:
        p_trans = parent_wall.get("transform", {})
        yaw = p_trans.get("rotation_y", 0.0)
    else:
        is_resolved = False

    center_y = sill_height_m + (height_m / 2.0)

    # 1. Window Glass Pane
    glass = trimesh.creation.box(extents=[width_m * 0.92, height_m * 0.92, 0.02])
    rot = trimesh.transformations.rotation_matrix(-yaw, [0, 1, 0])
    glass.apply_transform(rot)
    glass.apply_translation([wx, center_y, wz])
    glass.visual.vertex_colors = np.tile(COLOR_WINDOW_GLASS, (len(glass.vertices), 1))

    # 2. Outer Frame
    frame = trimesh.creation.box(extents=[width_m, height_m, 0.05])
    frame.apply_transform(rot)
    frame.apply_translation([wx, center_y, wz])
    frame.visual.vertex_colors = np.tile(COLOR_WINDOW_FRAME, (len(frame.vertices), 1))

    window_mesh = trimesh.util.concatenate([frame, glass])

    return {
        "id": window["id"],
        "type": "window",
        "wall_id": wall_id,
        "is_resolved": is_resolved,
        "source": "symbol_detector",
        "confidence": confidence,
        "status": status,
        "dimensions": {
            "width_m": round(width_m, 2),
            "height_m": round(height_m, 2),
            "sill_height_m": round(sill_height_m, 2)
        },
        "transform": {
            "position": [round(wx, 3), round(center_y, 3), round(wz, 3)],
            "rotation_y": round(yaw, 4),
        },
        "bounds": window_mesh.bounds.tolist(),
        "mesh": window_mesh
    }

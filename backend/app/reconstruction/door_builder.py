import math
import numpy as np
import trimesh
from typing import List, Dict, Any, Tuple, Optional

COLOR_DOOR_PANEL = [180, 83, 9, 255]    # Warm architectural wood
COLOR_DOOR_FRAME = [71, 85, 105, 255]   # Dark slate frame

def build_door_geometry(
    door: Dict[str, Any],
    wall_map: Dict[str, Dict[str, Any]],
    default_height: float = 2.10,
    default_width: float = 0.90,
    origin_offset: Tuple[float, float] = (0.0, 0.0)
) -> Dict[str, Any]:
    """
    Constructs 3D door frame and leaf panel assembly:
    - Associates door with parent wall segment orientation
    - If wall association is missing, flags as unresolved
    - Generates 3D door panel and frame meshes
    """
    wall_id = door.get("wall_id")
    parent_wall = wall_map.get(wall_id) if wall_id else None

    # Determine metric coordinates
    mp = door.get("metric_position")
    if mp:
        dx = mp[0] - origin_offset[0]
        dz = mp[1] - origin_offset[1]
    else:
        scale = 0.02
        pos = door.get("position", [0.0, 0.0])
        dx = pos[0] * scale - origin_offset[0]
        dz = pos[1] * scale - origin_offset[1]

    width_m = float(door.get("width_m") or default_width)
    height_m = float(door.get("height_m") or default_height)
    status = door.get("status", "OBSERVED")
    confidence = float(door.get("confidence") or 0.85)

    yaw = 0.0
    is_resolved = True

    if parent_wall:
        p_trans = parent_wall.get("transform", {})
        yaw = p_trans.get("rotation_y", 0.0)
        # Snap door position exactly to wall midpoint or segment axis
    else:
        is_resolved = False

    # 1. Door panel mesh
    panel = trimesh.creation.box(extents=[width_m * 0.95, height_m * 0.98, 0.04])
    rot = trimesh.transformations.rotation_matrix(-yaw, [0, 1, 0])
    panel.apply_transform(rot)
    panel.apply_translation([dx, height_m / 2.0, dz])
    panel.visual.vertex_colors = np.tile(COLOR_DOOR_PANEL, (len(panel.vertices), 1))

    # 2. Door frame jamb trim
    frame = trimesh.creation.box(extents=[width_m, height_m, 0.06])
    frame.apply_transform(rot)
    frame.apply_translation([dx, height_m / 2.0, dz])
    frame.visual.vertex_colors = np.tile(COLOR_DOOR_FRAME, (len(frame.vertices), 1))

    door_mesh = trimesh.util.concatenate([frame, panel])

    return {
        "id": door["id"],
        "type": "door",
        "wall_id": wall_id,
        "is_resolved": is_resolved,
        "source": "symbol_detector",
        "confidence": confidence,
        "status": status,
        "dimensions": {
            "width_m": round(width_m, 2),
            "height_m": round(height_m, 2),
        },
        "transform": {
            "position": [round(dx, 3), round(height_m / 2.0, 3), round(dz, 3)],
            "rotation_y": round(yaw, 4),
        },
        "bounds": door_mesh.bounds.tolist(),
        "mesh": door_mesh
    }
